import os
from flask import current_app
from datetime import datetime
from typing import Union, Dict, List, Optional, Any
from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
from database.database import get_db, get_database_schema_as_sql

class AI:
    def __init__(self, api_key: str):
        """Initialize the AI with API key and database connection."""
        if not api_key:
            raise ValueError("API key is required")
            
        self._client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=api_key
        )
        self._history: List[Dict[str, Any]] = []
        self._schema: str = get_database_schema_as_sql()
        self._last_sql: Optional[str] = None
        self._db_session_factory = get_db  # Store the session factory

    @property
    def history(self) -> List[Dict[str, Any]]:
        """Get a copy of the conversation history."""
        return self._history.copy()

    def _get_system_prompt(self) -> Dict[str, str]:
        """Generate the system prompt with database schema."""
        return {
            "role": "system",
            "content": f"""
            You are a MySQL expert analyzing this database:
            {self._schema}

            STRICT RULES:
            1. When using aggregate functions (COUNT, SUM, AVG, MIN, MAX):
            - All non-aggregated SELECT columns must be in GROUP BY
            - Never mix aggregated and non-aggregated columns without GROUP BY
            2. Follow ONLY_FULL_GROUP_BY rules
            3. Use backticks (`) for identifiers
            4. Return only valid MySQL SELECT queries
            5. Always include a LIMIT clause for safety if the amount of data is too big.
            6. Do not include any explanations, only the query ready to be executed, nothing else.
            7. Double check if the query is correct based on the database schema.
            8. Give the column names aliases that indicate exaclty what that value represents based on the user's question.
            """
        }

    def _add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the conversation history."""
        if role not in ["system", "user", "assistant"]:
            raise ValueError("Invalid role specified")
            
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            entry["metadata"] = metadata
        self._history.append(entry)

    def _clean_sql(self, sql: str) -> str:
        """Clean and standardize the SQL query format."""
        if not sql:
            raise ValueError("Empty SQL query")
            
        # Remove markdown code blocks
        for wrapper in ["```sql", "```"]:
            if sql.startswith(wrapper):
                sql = sql[len(wrapper):].strip()
            if sql.endswith(wrapper):
                sql = sql[:-len(wrapper)].strip()

        # Remove anything after semicolon and add one if missing
        if ';' in sql:
            sql = sql.split(';')[0].strip() + ';'
        else:
            sql = sql.strip() + ';'

        # Standardize identifier quotes
        sql = sql.replace('"', '`')

        # Validate it's a SELECT query by checking the first meaningful word
        first_word = sql.strip().split()[0].upper()
        if first_word != 'SELECT':
            raise ValueError(f"Only SELECT queries are allowed. Found: {first_word}")

        return sql.strip()

    def _validate_sql(self, sql: str) -> str:
        """Validate SQL syntax and ensure compliance with GROUP BY rules."""
        if not sql:
            raise ValueError("Empty SQL query")
            
        sql_upper = sql.upper()
        
        # Basic safety checks - block any potentially dangerous statements
        forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
                            "CREATE", "TRUNCATE", "GRANT", "REVOKE"]
        if any(f" {kw} " in f" {sql_upper} " for kw in forbidden_keywords):
            raise ValueError(f"Potentially dangerous operation detected: {sql}")
        
        # Check for aggregate functions
        has_aggregate = any(fn in sql_upper for fn in 
                        ['COUNT(', 'SUM(', 'AVG(', 'MIN(', 'MAX('])
        
        # Check for GROUP BY
        has_group_by = 'GROUP BY' in sql_upper
        
        if has_aggregate and not has_group_by:
            # Find all selected columns
            select_part = sql_upper.split('FROM')[0]
            columns = [col.strip() for col in select_part.replace('SELECT', '').split(',')]
            
            # Check for non-aggregated columns
            non_aggregated = [col for col in columns 
                            if not any(fn in col for fn in 
                                    ['COUNT(', 'SUM(', 'AVG(', 'MIN(', 'MAX('])]
            
            if non_aggregated:
                raise ValueError(
                    f"Missing GROUP BY for non-aggregated columns: {non_aggregated}\n"
                    "When using aggregate functions, all non-aggregated columns must be in GROUP BY"
                )
        
        # Ensure there's a LIMIT clause for safety
        if 'LIMIT' not in sql_upper:
            sql = sql.rstrip(';').strip() + " LIMIT 100;"
            
        return sql

    def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question with validation."""
        try:
            current_app.logger.debug(f"Generating SQL for question: {question}")
            
            messages = [
                self._get_system_prompt(),
                {"role": "user", "content": f"Create MySQL query for: {question}\n"
                "Important: Follow ONLY_FULL_GROUP_BY rules and include a LIMIT clause"}
            ]
            
            response = self._client.chat.completions.create(
                model='deepseek/deepseek-chat:free',
                messages=messages,
                temperature=0.1
            )
            
            # Properly handle the API response
            if not response.choices or not response.choices[0].message:
                raise ValueError("Resposta vazia da IA recebida. Isso pode significar que a cota diária foi excedida.")
                
            raw_sql = response.choices[0].message.content
            if not raw_sql:
                raise ValueError("Nenhum SQL foi gerado na resposta.")
                
            current_app.logger.debug(f"Raw SQL received: {raw_sql}")
            
            clean_sql = self._clean_sql(raw_sql)
            validated_sql = self._validate_sql(clean_sql)
            
            self._last_sql = validated_sql
            return validated_sql
        
        except Exception as e:
            error_msg = f"Erro ao gerar SQL: {str(e)}"
            current_app.logger.error(f"SQL Generation Error: {error_msg}")
            self._add_to_history("system", error_msg, {"error": True})
            raise Exception(error_msg)

    def execute_query(self, sql: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a validated SQL query and return results."""
        if not sql and not self._last_sql:
            raise ValueError("Nenhum SQL foi dado ou gerado.")
            
        sql_to_execute = sql if sql else self._last_sql
        
        if not sql_to_execute:
            raise ValueError("Nenhuma query SQL válida a ser executada.")
            
        if sql and sql != self._last_sql:
            raise ValueError("Query validation failed - only use generated SQL")
        
        db: Optional[scoped_session] = None
        try:
            db = self._db_session_factory()
            result = db.execute(text(sql_to_execute))
            
            if not result.returns_rows:
                return []
                
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            self._add_to_history("system", f"Query execution failed: {error_msg}", {"error": True})
            raise Exception(f"Database error: {error_msg}")
        finally:
            if db:
                db.remove()

    def explain_results(self, question: str, results: List[Dict]) -> str:
        """Generate natural language explanation of query results."""
        if not question:
            raise ValueError("Uma pergunta é requerida para uma explicação.")
            
        prompt = f"""
        Pergunta original: {question}
        Dados encontrados (apenas os primeiros 3 registros): {str(results[:3]) if results else "Nenhum dado encontrado"}
        
        Forneça uma resposta direta em português que:
        1. Responda à pergunta original
        2. Responda somente à pergunta original, use os dados fornecidos apenas para fazer a análise solicitada.
        3. Não repita os dados literalmente, SOMENTE SE o usuário solicitar
        4. Seja conciso e claro
        5. Se não houver resultados, explique por que isso pode ter acontecido, mas APENAS se não houver
        6. Se o usuário solicitar qualquer dado sensível, apenas responda 'Não tenho autorização para fornecer estes dados'
        7. Apenas explique análises relacionadas à pesagem ou aos animais, qualquer pergunta fora deste contexto deve ser rejeitada.
        8. Em HIPÓTESE ALGUMA forneca dados de usuário como resposta.
        9. Qualquer pergunta sobre usuários deve ser rejeitada, você não está autorizado a fornecer nenhum dados sensível e nem discorrer sobre eles.
        10. Você pode fornecer quaisquer dados brutos fora os dados de usuários e outros dados sensíveis.
        11. Use todas as interações anteriores como base para resposta final
        """
        
        try:
            response = self._client.chat.completions.create(
                model='deepseek/deepseek-chat:free',
                messages=[
                    {"role": "system", "content": "Você é um analista de dados respondendo em português."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            explanation = response.choices[0].message.content.strip()
            self._add_to_history("assistant", explanation)
            return explanation
            
        except Exception as e:
            error_msg = f"Falha ao gerar explicação: {str(e)}"
            self._add_to_history("system", error_msg, {"error": True})
            return error_msg

    def ask_about_data(self, question: str) -> str:
        """Complete Q&A flow from question to natural language answer."""
        if not question or not isinstance(question, str):
            raise ValueError("Question must be a non-empty string")
            
        try:
            self._add_to_history("user", question)
            
            # Step 1: Generate SQL
            sql = self.generate_sql(question)
            self._add_to_history("system", f"Generated SQL: {sql}", {"sql": sql})
            
            # Step 2: Execute query
            results = self.execute_query(sql)
            self._add_to_history("system", f"Found {len(results)} results", {"result_count": len(results)})
            
            # Step 3: Explain results
            response = self.explain_results(question, results)
            
            return response, sql
            
        except Exception as e:
            error_msg = f"Erro: {str(e)}"
            self._add_to_history("system", error_msg, {"error": True})
            return error_msg

    def prompt(self, msg: str) -> str:
        """General chat prompt that maintains conversation context."""
        if not msg or not isinstance(msg, str):
            raise ValueError("Message must be a non-empty string")
            
        self._add_to_history("user", msg)
        
        try:
            response = self._client.chat.completions.create(
                model='deepseek/deepseek-chat:free',
                messages=[
                    *[{"role": h["role"], "content": h["content"]} 
                      for h in self._history 
                      if h["role"] != "system"],
                    {"role": "user", "content": msg}
                ]
            )
            
            reply = response.choices[0].message.content
            self._add_to_history("assistant", reply)
            return reply
            
        except Exception as e:
            error_msg = f"Falha na comunicação com o modelo: {str(e)}"
            self._add_to_history("system", error_msg, {"error": True})
            return error_msg