from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class MataKuliah(Base):
    __tablename__ = "mata_kuliah"

    id = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(100), nullable=False, unique=True, index=True)
    nama_mk = Column(String(255), nullable=False)
    sks = Column(Integer, nullable=False)
    prodi_id = Column(Integer, ForeignKey("prodi.id"), nullable=True)

    prodi = relationship("Prodi", back_populates="mata_kuliah")
    krs = relationship("KRS", back_populates="mata_kuliah")
