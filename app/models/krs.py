from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class KRS(Base):
    __tablename__ = "krs"

    id = Column(Integer, primary_key=True, index=True)

    mahasiswa_id = Column(
        Integer,
        ForeignKey("mahasiswa.id"),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey("course.id"),
        nullable=False
    )

    semester = Column(Integer, nullable=False)

    # Relasi ke Mahasiswa
    mahasiswa = relationship(
        "Mahasiswa",
        back_populates="krs"
    )

    # Relasi ke Course
    course = relationship(
        "Course",
        back_populates="krs"
    )

    # Relasi ke Grade
    grade = relationship(
        "Grade",
        back_populates="krs",
        uselist=False
    )