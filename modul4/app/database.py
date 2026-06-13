import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Mengambil URL dari docker-compose, jika tidak ada pakai localhost (untuk dev lokal)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/llm_chat_db")

# pool_pre_ping=True mencegah error koneksi terputus saat aplikasi jalan di Docker
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()