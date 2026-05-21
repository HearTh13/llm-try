from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class MataKuliah(Base):
    __tablename__ = "mata_kuliah"

    id = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(100), nullable=False, unique=True, index=True)
    nama_mk = Column(String(255), nullable=False)
    sks = Column(Integer, nullable=False)

    krs = relationship("KRS", back_populates="mata_kuliah")
