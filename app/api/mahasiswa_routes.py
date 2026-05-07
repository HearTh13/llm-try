from schemas.requests import MahasiswaRequest

from fastapi import APIRouter

router = APIRouter()

data_mahasiswa = []

@router.post("/mahasiswa")
def insert_mahasiswa(request: MahasiswaRequest):

    mahasiswa_baru = {
        "nim": request.nim,
        "nama": request.nama,
        "jurusan": request.jurusan,
        "semester": request.semester
    }

    data_mahasiswa.append(mahasiswa_baru)

    return {
        "message": "Data mahasiswa berhasil ditambahkan",
        "data": mahasiswa_baru
    }