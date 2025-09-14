from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(url=db_url)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


def get_database():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print("Error:", e)
        raise e
    finally:
        db.close()


import models
