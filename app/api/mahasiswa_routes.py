from app.schemas.requests import MahasiswaRequest
from app.services.mahasiswa_service import MahasiswaService
from app.database import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

data_mahasiswa = []

@router.post("/mahasiswa")
def insert_mahasiswa(request: MahasiswaRequest, db: Session = Depends(get_db)):

    mahasiswa_baru = {
        "nim": request.nim,
        "nama": request.nama,
        "jurusan": request.jurusan,
        "semester": request.semester
    }

    data_mahasiswa.append(mahasiswa_baru)
    
    create_mahasiswa = MahasiswaService.create_mahasiswa(
        db=db,
        data=mahasiswa_baru
    )
    

    return {
        "message": "Data mahasiswa berhasil ditambahkan",
        "data": mahasiswa_baru
    }
    
@router.get("/mahasiswa")
def get_all_mahasiswa(db: Session = Depends(get_db)):

    mahasiswa = MahasiswaService.get_all_mahasiswa(db)

    return {
        "message": "Data mahasiswa berhasil diambil",
        "data": mahasiswa
    }
    
@router.get("/mahasiswa/{mahasiswa_id}")
def get_mahasiswa_by_id(mahasiswa_id: int, db: Session = Depends(get_db)):

    mahasiswa = MahasiswaService.get_mahasiswa_by_id(
        db=db,
        mahasiswa_id=mahasiswa_id
    )

    return {
        "message": "Data mahasiswa berhasil diambil",
        "data": mahasiswa
    }
    
@router.put("/mahasiswa/{mahasiswa_id}")
def update_mahasiswa(mahasiswa_id: int, request: MahasiswaRequest, db: Session = Depends(get_db)):

    mahasiswa_update = {
        "nim": request.nim,
        "nama": request.nama,
        "jurusan": request.jurusan,
        "semester": request.semester
    }

    update_mahasiswa = MahasiswaService.update_mahasiswa(
        db=db,
        mahasiswa_id=mahasiswa_id,
        data=mahasiswa_update
    )

    return {
        "message": "Data mahasiswa berhasil diupdate",
        "data": update_mahasiswa
    }
    
@router.delete("/mahasiswa/{mahasiswa_id}")
def delete_mahasiswa(mahasiswa_id: int, db: Session = Depends(get_db)):

    delete_mahasiswa = MahasiswaService.delete_mahasiswa(
        db=db,
        mahasiswa_id=mahasiswa_id
    )

    return {
        "message": "Data mahasiswa berhasil dihapus",
        "data": delete_mahasiswa
    }