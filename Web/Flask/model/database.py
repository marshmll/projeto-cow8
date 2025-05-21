from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.schema import CreateTable

DATABASE_URI = "mysql+mysqlconnector://client:bancodedados@localhost:3307/cow8_db"

engine = create_engine(DATABASE_URI, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    return scoped_session(SessionLocal)