from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Mahasiswa(Base):
    __tablename__ = "mahasiswa"

    id = Column(Integer, primary_key=True, index=True)
    nim = Column(String(100), nullable=False)
    nama = Column(String(255), nullable=False)
    jurusan = Column(String(255), nullable=False)
    semester = Column(Integer, nullable=False)

    # Relasi ke tabel KRS
    krs = relationship("KRS", back_populates="mahasiswa")