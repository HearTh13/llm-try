from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.building import Building
from app.models.schemas import BuildingCreate, BuildingResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=BuildingResponse)
def tambah_bangunan(bangunan: BuildingCreate, db: Session = Depends(get_db)):
    db_bangunan = Building(**bangunan.model_dump())
    db.add(db_bangunan)
    db.commit()
    db.refresh(db_bangunan)
    return db_bangunan

@router.get("/", response_model=List[BuildingResponse])
def lihat_semua_bangunan(db: Session = Depends(get_db)):
    return db.query(Building).all()