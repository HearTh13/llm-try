from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    prompt: str
    jawaban_ai: str

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

class FacultyBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class FacultyCreate(FacultyBase):
    pass

class FacultyResponse(FacultyBase):
    id: int

    class Config:
        from_attributes = True

class StudyProgramBase(BaseModel):
    faculty_id: int
    name: str
    degree: str
    description: Optional[str] = None
    accreditation: Optional[str] = None
    image_url: Optional[str] = None

class StudyProgramCreate(StudyProgramBase):
    pass

class StudyProgramResponse(StudyProgramBase):
    id: int

    class Config:
        from_attributes = True

class BuildingBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None

class BuildingCreate(BuildingBase):
    pass

class BuildingResponse(BuildingBase):
    id: int

    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    date: datetime = Field(default_factory=datetime.now)

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    id: int

    class Config:
        from_attributes = True