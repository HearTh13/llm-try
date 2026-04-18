from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # fakultas, perpustakaan, masjid, lab, parkir

    description = Column(Text)
    address = Column(String(255))

    latitude = Column(Float)
    longitude = Column(Float)

    image_url = Column(String(500))