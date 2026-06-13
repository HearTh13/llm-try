"""
Utilitas autentikasi: hashing password (PBKDF2, stdlib) + token JWT (PyJWT) +
dependency FastAPI untuk mengambil user dari header Authorization.
"""
import os
import hmac
import hashlib
import binascii
import datetime

import jwt
from fastapi import Depends, HTTPException, Header

JWT_SECRET = os.getenv("JWT_SECRET", "ganti-secret-ini-di-produksi-modul4")
JWT_ALG = "HS256"
TOKEN_HOURS = 12


# ----------------------------- Password hashing -----------------------------

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return binascii.hexlify(salt).decode() + "$" + binascii.hexlify(dk).decode()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split("$")
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), dk_hex)
    except Exception:
        return False


# --------------------------------- JWT token --------------------------------

def create_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_HOURS)
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


# ------------------------------ FastAPI deps ---------------------------------

def _extract(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return decode_token(authorization.split(" ", 1)[1])
    except Exception:
        return None


def get_current_user(authorization: str = Header(None)) -> dict:
    user = _extract(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Token tidak ada / tidak valid / kadaluarsa.")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak: khusus admin/sekretariat.")
    return user


def get_optional_user(authorization: str = Header(None)):
    """Kembalikan user dict jika token valid, atau None bila tidak ada. Tidak melempar error."""
    return _extract(authorization)
