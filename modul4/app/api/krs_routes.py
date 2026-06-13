from app.schemas.requests import KrsRequest
from app.services.krs_service import KrsService
from app.database import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/krs")
def insert_krs(request: KrsRequest, db: Session = Depends(get_db)):
    return KrsService.create_krs(db=db, data=request.model_dump())


@router.get("/krs")
def get_all_krs(db: Session = Depends(get_db)):
    return KrsService.get_all_krs(db)


@router.get("/krs/{krs_id}")
def get_krs_by_id(krs_id: int, db: Session = Depends(get_db)):
    return KrsService.get_krs_by_id(db=db, krs_id=krs_id)


@router.put("/krs/{krs_id}")
def update_krs(krs_id: int, request: KrsRequest, db: Session = Depends(get_db)):
    return KrsService.update_krs(db=db, krs_id=krs_id, data=request.model_dump())


@router.delete("/krs/{krs_id}")
def delete_krs(krs_id: int, db: Session = Depends(get_db)):
    return KrsService.delete_krs(db=db, krs_id=krs_id)
