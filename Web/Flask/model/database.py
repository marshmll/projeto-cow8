from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
import os

if (os.environ.get("STAGING") is not None):
    DATABASE_URI = 'mysql+mysqlconnector://localhost:localhost@localhost:3307/cow8_db'
else:
    DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        query={"unix_socket": "/cloudsql/" + os.environ.get('DB_URL')},
    )

engine = create_engine(
    DATABASE_URI,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    return scoped_session(SessionLocal)