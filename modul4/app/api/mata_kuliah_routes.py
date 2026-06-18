from app.schemas.requests import MataKuliahRequest
from app.services.mata_kuliah_service import MataKuliahService
from app.database import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/mata_kuliah")
def insert_mata_kuliah(request: MataKuliahRequest, db: Session = Depends(get_db)):
    return MataKuliahService.create_mata_kuliah(db=db, data=request.model_dump())


@router.get("/mata_kuliah")
def get_all_mata_kuliah(db: Session = Depends(get_db)):
    return MataKuliahService.get_all_mata_kuliah(db)


@router.get("/mata_kuliah/{mk_id}")
def get_mata_kuliah_by_id(mk_id: int, db: Session = Depends(get_db)):
    return MataKuliahService.get_mata_kuliah_by_id(db=db, mk_id=mk_id)


@router.put("/mata_kuliah/{mk_id}")
def update_mata_kuliah(mk_id: int, request: MataKuliahRequest, db: Session = Depends(get_db)):
    return MataKuliahService.update_mata_kuliah(db=db, mk_id=mk_id, data=request.model_dump())


@router.delete("/mata_kuliah/{mk_id}")
def delete_mata_kuliah(mk_id: int, db: Session = Depends(get_db)):
    return MataKuliahService.delete_mata_kuliah(db=db, mk_id=mk_id)
