from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.news import News
from app.models.schemas import NewsCreate, NewsResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NewsResponse)
def tambah_berita(news: NewsCreate, db: Session = Depends(get_db)):
    db_news = News(**news.model_dump())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@router.get("/", response_model=List[NewsResponse])
def lihat_semua_berita(db: Session = Depends(get_db)):
    return db.query(News).all()