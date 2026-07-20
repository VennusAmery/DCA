import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

required_env_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ImportError(
        f"Error: Faltan las siguientes variables en tu archivo .env: {', '.join(missing_vars)}"
    )

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


def init_db():
    """Crea las tablas si no existen. Correr una vez al iniciar el proyecto."""
    from database import models 
    Base.metadata.create_all(bind=engine)