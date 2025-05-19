import os

from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
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
    Based on the table schema below, write a SQL query (in plaintext, ready to be copied and pasted in a terminal to execute it, never surrounded by backticks) that would answer the user's question:

    {schema}

    Question: {question}
    SQL Query:"""
    prompt_sql = ChatPromptTemplate.from_template(template_sql)

    llm = ChatOpenRouter(model_name="deepseek/deepseek-chat:free")
    sql_chain = (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt_sql
        | llm.bind(stop=['\nSQLResult:'])
        | StrOutputParser()
    )

    template_response = """Based on the table schema below, question, sql query, and sql response, now write a natural language response (in the same language of the question):
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}"""
    prompt_response = ChatPromptTemplate.from_template(template_response)

    full_chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=get_schema,
            response=lambda vars: run_query(vars['query']),
        )
        | prompt_response
        | llm.bind(stop=['\nNatural Language Response:'])
    )

    def __init__(self):
        pass

    def prompt(self, question: str) -> AIMessage:
        return self.full_chain.invoke({'question': question})
