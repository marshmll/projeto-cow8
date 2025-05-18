from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.schema import CreateTable

DATABASE_URL = "mysql+mysqlconnector://client:bancodedados@localhost:3307/cow8_db"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

metadata = MetaData()
    
# Reflect all tables from the database
metadata.reflect(bind=engine)

def get_db():
    return scoped_session(SessionLocal)

def get_database_schema_as_sql(): 
    schema_sql = ""
    
    # Generate CREATE TABLE statements for each table
    for table in metadata.sorted_tables:
        # Skip alembic version table if it exists
        if table.name == 'alembic_version':
            continue
            
        create_table_sql = str(CreateTable(table).compile(engine))
        schema_sql += f"{create_table_sql};\n\n"
    
    return schema_sql.strip()