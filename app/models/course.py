from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(100), nullable=False)
    nama_mk = Column(String(255), nullable=False)
    sks = Column(Integer, nullable=False)

    # Relasi ke tabel KRS
    krs = relationship("KRS", back_populates="course")