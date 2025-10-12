# app/api/src/app/db.py
from sqlmodel import SQLModel, create_engine, Session
import os

# Read DATABASE_URL from env; default is fine for docker-compose-internal
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://appuser:apppass@db:5432/oadb"
)

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session
