from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from utils.chat_open_router import ChatOpenRouter

from model.database import DATABASE_URI

db = SQLDatabase.from_uri(DATABASE_URI)

def get_schema(_):
    return db.get_table_info()

def run_query(query):
    return db.run(query)

class DatabaseAIAssistant():
    template_sql = """
    Based on the table schema below, write a SQL query that would answer the user's question.
    Follow these STRICT rules:
    1. Use only standard MySQL 8.0.32 syntax - avoid window functions not supported in MySQL
    2. Never use PERCENTILE_CONT, WITHIN GROUP, or other advanced analytics functions
    3. For median calculations, use a simple approach with COUNT and LIMIT
    4. For mode calculations, use GROUP BY with COUNT and ORDER BY
    5. Always include proper GROUP BY clauses for aggregate queries
    6. Never include comments or explanations
    7. Output only the raw SQL query, no backticks or markers
    8. Verify the query syntax is valid before returning it
    9. Use only tables and columns that exist in the schema
    10. Include all required JOIN conditions
    11. Make sure SQLAlchemy can run the query without issues

    Schema:
    {schema}

    Question: {question}

    Valid MySQL Query:"""
    prompt_sql = ChatPromptTemplate.from_template(template_sql)

    template_response = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
    1. Use the same language as the question
    2. Only report facts from the SQL response
    3. Never mention SQL or the query itself
    4. Format numbers appropriately
    5. Keep response concise but informative
    6. Do not include any code, links, or technical details
    7. Detail your explanation of the data if the user requested
    8. You can use basic markdown, headers or lists to organize your answer

    Schema:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}

    Natural Language Response:"""
    prompt_response = ChatPromptTemplate.from_template(template_response)

    template_graphic = """Generate a Chart.js visualization based on this data:
    1. Output ONLY the raw canvas element and self-executing script
    2. No HTML, body, backticks or other wrapper tags
    3. No explanations or comments
    4. Generate a unique canvas ID based on the question
    5. Use appropriate chart type for the data
    6. Include proper labels and formatting
    7. Assume Chart.js is already loaded
    8. Make the visualization responsive
    9. Use a color scheme that works on dark backgrounds

    Schema:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}

    Chart.js Implementation:"""
    prompt_graphic = ChatPromptTemplate.from_template(template_graphic)

    def __init__(self):
        self.llm = ChatOpenRouter(model_name="deepseek/deepseek-chat:free")
        
        # SQL generation chain
        self.sql_generation_chain = (
            RunnablePassthrough.assign(schema=get_schema)
            | self.prompt_sql
            | self.llm.bind(stop=['\nSQLResult:'])
            | StrOutputParser()
        )
        
        # Full execution chain
        self.full_chain = (
            RunnablePassthrough.assign(
                schema=get_schema,
                query=self.sql_generation_chain,
            )
            .assign(
                response=lambda x: self._safe_run_query(x["query"])
            )
        )

    def _safe_run_query(self, query: str):
        """Execute query with additional validation and error handling"""
        try:
            # Basic validation checks
            if not query or not query.strip():
                raise ValueError("Empty query generated")
                
            if ";" in query.rstrip(";"):  # Multiple statements
                raise ValueError("Query contains multiple statements")
                
            # Check for forbidden patterns
            forbidden_patterns = [
                'PERCENTILE_CONT', 'WITHIN GROUP', 'FILTER', 
                'OVER', 'PARTITION BY', 'LATERAL VIEW'
            ]
            if any(patt in query.upper() for patt in forbidden_patterns):
                raise ValueError(f"Query contains unsupported MySQL function")
                
            return db.run(query)
            
        except Exception as e:
            print(f"Query execution failed: {e}\nQuery: {query}")
            raise ValueError(f"Invalid SQL query generated: {str(e)}") from e

    def _needs_graphic(self, question: str) -> bool:
        """Determine if the user's question implies they want a graphic/chart."""
        graphic_keywords = [
            # Common terms for charts/graphs
            'gráfico', 'gráficos', 'grafico', 'graficos',
            'chart', 'charts',  # English terms commonly used in PT-BR too
            'visualização', 'visualizacao', 'visualizar',
            'plot', 'plotar',  # Used in technical contexts
            'diagrama', 'desenho', 'figura', 'imagem',
            
            # Chart types
            'barras', 'barra',
            'linha', 'linhas',
            'pizza', 'setores', 'circular',
            'histograma', 'dispersão', 'área',
            
            # Action verbs/phrases
            'mostre me', 'mostrar', 'mostre um',
            'exibir', 'ver', 'visualizar',
            'como está', 'como estão', 
            'evolução', 'tendência', 'comparação',
            'ao longo do tempo', 'por período',
            
            # Question patterns
            'tem um gráfico', 'tem gráfico',
            'pode mostrar um gráfico',
            'quero ver um gráfico',
            'mostre graficamente',
            
            # Data representation
            'dados em forma de',
            'representação visual',
            'forma gráfica'
        ]
        
        # Remove accents and make lowercase for more robust matching
        question_normalized = (question.lower()
                            .replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
                            .replace('é', 'e').replace('ê', 'e')
                            .replace('í', 'i').replace('î', 'i')
                            .replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
                            .replace('ú', 'u').replace('û', 'u')
                            .replace('ç', 'c'))
        
        return any(keyword in question_normalized for keyword in graphic_keywords)

    def prompt(self, question: str) -> dict:
        """Process the question with error handling"""
        try:
            # Get base data (query, schema, response)
            chain_data = self.full_chain.invoke({"question": question})
            
            if not chain_data.get("query") or not chain_data.get("response"):
                raise ValueError("Failed to generate valid SQL or get database response")
            
            # Generate responses
            result = {
                "response": self.llm.invoke(
                    self.prompt_response.format_messages(
                        question=question,
                        query=chain_data["query"],
                        response=chain_data["response"],
                        schema=chain_data["schema"]
                    )
                ).content,
                "query": chain_data["query"],
                "success": True
            }
            
            # Add graphic if needed
            if self._needs_graphic(question):
                try:
                    result["graphic"] = self.llm.invoke(
                        self.prompt_graphic.format_messages(**chain_data)
                    ).content
                except Exception as e:
                    print(f"Graphic generation failed: {e}")
                    result["graphic"] = None
                    
            return result
            
        except ValueError as ve:
            # Handle SQL-specific errors
            error_msg = str(ve)
            if "Invalid SQL" in error_msg or "syntax" in error_msg.lower():
                return {
                    "response": "Ocorreu um erro na geração da consulta SQL. Por favor, reformule sua pergunta.",
                    "graphic": None,
                    "query": "",
                    "success": False,
                    "error": error_msg
                }
            else:
                return {
                    "response": "Não foi possível processar sua solicitação no momento.",
                    "graphic": None,
                    "query": "",
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            # General error handling
            print(f"Unexpected error: {e}")
            return {
                "response": "Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.",
                "graphic": None,
                "query": "",
                "success": False,
                "error": str(e)
            }