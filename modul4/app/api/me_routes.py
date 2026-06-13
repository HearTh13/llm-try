"""
Endpoint data milik mahasiswa yang sedang login (scoped via token).
Mahasiswa HANYA bisa melihat datanya sendiri, tidak bisa data mahasiswa lain.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_utils import get_current_user
from app.models.mahasiswa import Mahasiswa
from app.models.krs import KRS
from app.models.mata_kuliah import MataKuliah

router = APIRouter()

BOBOT = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}


def _current_student(user: dict, db: Session) -> Mahasiswa:
    if user.get("role") != "mahasiswa" or not user.get("mahasiswa_id"):
        raise HTTPException(status_code=403, detail="Endpoint ini khusus akun mahasiswa.")
    m = db.query(Mahasiswa).filter(Mahasiswa.id == user["mahasiswa_id"]).first()
    if not m:
        raise HTTPException(status_code=404, detail="Data mahasiswa tidak ditemukan.")
    return m


@router.get("/profile")
def my_profile(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    m = _current_student(user, db)
    return {"id": m.id, "nim": m.nim, "nama": m.nama, "jurusan": m.jurusan, "semester": m.semester}


@router.get("/krs")
def my_krs(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    m = _current_student(user, db)
    rows = (
        db.query(KRS, MataKuliah)
        .join(MataKuliah, KRS.mata_kuliah_id == MataKuliah.id)
        .filter(KRS.mahasiswa_id == m.id)
        .order_by(KRS.semester_diambil)
        .all()
    )
    data = [
        {
            "semester_diambil": k.semester_diambil,
            "kode_mk": mk.kode_mk,
            "nama_mk": mk.nama_mk,
            "sks": mk.sks,
            "nilai_huruf": k.nilai_huruf,
        }
        for k, mk in rows
    ]
    return {"data": data}


@router.get("/summary")
def my_summary(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    m = _current_student(user, db)
    rows = (
        db.query(KRS, MataKuliah)
        .join(MataKuliah, KRS.mata_kuliah_id == MataKuliah.id)
        .filter(KRS.mahasiswa_id == m.id)
        .all()
    )
    total_sks_dinilai = 0
    total_mutu = 0
    sks_lulus = 0
    for k, mk in rows:
        if k.nilai_huruf in BOBOT:
            total_sks_dinilai += mk.sks
            total_mutu += mk.sks * BOBOT[k.nilai_huruf]
            if k.nilai_huruf != "E":
                sks_lulus += mk.sks
    ipk = round(total_mutu / total_sks_dinilai, 2) if total_sks_dinilai else 0.0
    return {
        "nim": m.nim,
        "nama": m.nama,
        "semester": m.semester,
        "ipk": ipk,
        "sks_lulus": sks_lulus,
        "total_sks_dinilai": total_sks_dinilai,
    }
