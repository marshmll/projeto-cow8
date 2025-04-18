from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

DATABASE_URL = "mysql+mysqlconnector://client:bancodedados@db:3306/cow8_db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()