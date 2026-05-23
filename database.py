from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/taskapp"
)

Base = declarative_base()
db_available = False
db_error_message = ""
engine = None
SessionLocal = None

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
        pool_timeout=5,
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_available = True
    logger.info("Banco de dados conectado com sucesso.")
except Exception as e:
    db_error_message = str(e)
    logger.error(f"Falha ao conectar ao banco de dados: {e}")


def get_db():
    if not db_available or SessionLocal is None:
        raise RuntimeError("Banco de dados indisponível")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_optional():
    if not db_available or SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
