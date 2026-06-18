from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class User(Base):
    """
    Akun login. Dua role:
      - 'admin'     : petugas/sekretariat, akses penuh CRUD + kelola dokumen.
      - 'mahasiswa' : login pakai NIM, terhubung ke baris di tabel mahasiswa.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' | 'mahasiswa'
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.id"), nullable=True)
