from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base

class StudyProgram(Base):
    __tablename__ = "study_programs"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, nullable=False)

    name = Column(String(100), nullable=False)
    degree = Column(String(20), nullable=False)  # D3, S1, S2, S3
    description = Column(Text)
    accreditation = Column(String(20))
    image_url = Column(String(500))