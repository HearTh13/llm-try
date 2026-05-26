from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Prodi(Base):
    __tablename__ = "prodi"

    id = Column(Integer, primary_key=True, index=True)
    fakultas_id = Column(Integer, ForeignKey("fakultas.id"), nullable=False)
    nama = Column(String(255), nullable=False)
    jenjang = Column(String(50), nullable=False) # e.g. S1, S2, D3

    fakultas = relationship("Fakultas", back_populates="prodi")
    mata_kuliah = relationship("MataKuliah", back_populates="prodi")
