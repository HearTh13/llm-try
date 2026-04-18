import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Mengambil URL dari docker-compose, jika tidak ada pakai localhost (untuk dev lokal)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/llm_chat_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()