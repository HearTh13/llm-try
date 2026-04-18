from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base

class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    image_url = Column(String(500))