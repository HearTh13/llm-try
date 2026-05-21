from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Mahasiswa(Base):
    __tablename__ = "mahasiswa"

    id = Column(Integer, primary_key=True, index=True)
    nim = Column(String(100), nullable=False, unique=True, index=True)
    nama = Column(String(255), nullable=False)
    prodi_id = Column(Integer, ForeignKey("prodi.id"), nullable=False)
    semester = Column(Integer, nullable=False)

    prodi = relationship("Prodi", back_populates="mahasiswa")
    krs = relationship("KRS", back_populates="mahasiswa")
