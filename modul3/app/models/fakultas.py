from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Fakultas(Base):
    __tablename__ = "fakultas"

    id = Column(Integer, primary_key=True, index=True)
    singkatan = Column(String(50), nullable=False, unique=True)
    nama = Column(String(255), nullable=False)

    prodi = relationship("Prodi", back_populates="fakultas")
