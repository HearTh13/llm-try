from app.schemas.requests import MahasiswaRequest
from app.services.mahasiswa_service import MahasiswaService
from app.database import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/mahasiswa")
def insert_mahasiswa(
    request: MahasiswaRequest,
    db: Session = Depends(get_db)
):

    mahasiswa_baru = {
        "nim": request.nim,
        "nama": request.nama,
        "jurusan": request.jurusan,
        "semester": request.semester
    }

    result = MahasiswaService.create_mahasiswa(
        db=db,
        data=mahasiswa_baru
    )

    return result


@router.get("/mahasiswa")
def get_all_mahasiswa(
    db: Session = Depends(get_db)
):

    result = MahasiswaService.get_all_mahasiswa(db)

    return result


@router.get("/mahasiswa/{mahasiswa_id}")
def get_mahasiswa_by_id(
    mahasiswa_id: int,
    db: Session = Depends(get_db)
):

    result = MahasiswaService.get_mahasiswa_by_id(
        db=db,
        mahasiswa_id=mahasiswa_id
    )

    return result


@router.put("/mahasiswa/{mahasiswa_id}")
def update_mahasiswa(
    mahasiswa_id: int,
    request: MahasiswaRequest,
    db: Session = Depends(get_db)
):

    mahasiswa_update = {
        "nim": request.nim,
        "nama": request.nama,
        "jurusan": request.jurusan,
        "semester": request.semester
    }

    result = MahasiswaService.update_mahasiswa(
        db=db,
        mahasiswa_id=mahasiswa_id,
        data=mahasiswa_update
    )

    return result


@router.delete("/mahasiswa/{mahasiswa_id}")
def delete_mahasiswa(
    mahasiswa_id: int,
    db: Session = Depends(get_db)
):

    result = MahasiswaService.delete_mahasiswa(
        db=db,
        mahasiswa_id=mahasiswa_id
    )

    return result