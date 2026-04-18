from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.faculty import Faculty
from app.models.schemas import FacultyCreate, FacultyResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FacultyResponse)
def tambah_fakultas(faculty: FacultyCreate, db: Session = Depends(get_db)):
    db_faculty = Faculty(**faculty.model_dump())
    db.add(db_faculty)
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@router.get("/", response_model=List[FacultyResponse])
def lihat_semua_fakultas(db: Session = Depends(get_db)):
    return db.query(Faculty).all()