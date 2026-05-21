from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class KRS(Base):
    __tablename__ = "krs"

    id = Column(Integer, primary_key=True, index=True)
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.id"), nullable=False)
    mata_kuliah_id = Column(Integer, ForeignKey("mata_kuliah.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    nilai_huruf = Column(String(2), nullable=True) # A, B, C, D, E

    mahasiswa = relationship("Mahasiswa", back_populates="krs")
    mata_kuliah = relationship("MataKuliah", back_populates="krs")
