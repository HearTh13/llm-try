from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.mahasiswa import Mahasiswa
from app.auth_utils import verify_password, create_token, get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password salah.")

    nim = None
    nama = None
    if user.mahasiswa_id:
        m = db.query(Mahasiswa).filter(Mahasiswa.id == user.mahasiswa_id).first()
        if m:
            nim = m.nim
            nama = m.nama

    token = create_token({
        "sub": user.username,
        "role": user.role,
        "nim": nim,
        "mahasiswa_id": user.mahasiswa_id,
    })
    return {
        "token": token,
        "role": user.role,
        "username": user.username,
        "nim": nim,
        "nama": nama,
    }


@router.get("/me")
def whoami(user: dict = Depends(get_current_user)):
    return {
        "username": user.get("sub"),
        "role": user.get("role"),
        "nim": user.get("nim"),
        "mahasiswa_id": user.get("mahasiswa_id"),
    }
