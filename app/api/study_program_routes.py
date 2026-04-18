from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.study_program import StudyProgram
from app.models.schemas import StudyProgramCreate, StudyProgramResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=StudyProgramResponse)
def tambah_prodi(prodi: StudyProgramCreate, db: Session = Depends(get_db)):
    db_prodi = StudyProgram(**prodi.model_dump())
    db.add(db_prodi)
    db.commit()
    db.refresh(db_prodi)
    return db_prodi

@router.get("/", response_model=List[StudyProgramResponse])
def lihat_semua_prodi(db: Session = Depends(get_db)):
    return db.query(StudyProgram).all()