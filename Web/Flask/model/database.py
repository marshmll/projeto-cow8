from sqlalchemy import create_engine, MetaData, URL
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.schema import CreateTable
import os



DATABASE_URI = URL.create(
    drivername="mysql+pymysql",
    username=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    database=os.environ.get('DB_NAME'),
    query={"unix_socket": "/cloudsql/" + os.environ.get('DB_URL')},
)

engine = create_engine(
    DATABASE_URI,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    return scoped_session(SessionLocal)