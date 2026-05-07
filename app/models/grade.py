from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Grade(Base):
    __tablename__ = "grade"

    id = Column(Integer, primary_key=True, index=True)

    krs_id = Column(
        Integer,
        ForeignKey("krs.id"),
        nullable=False
    )

    nilai = Column(String(10), nullable=False)
    keterangan = Column(String(255), nullable=False)

    # Relasi ke KRS
    krs = relationship(
        "KRS",
        back_populates="grade"
    )