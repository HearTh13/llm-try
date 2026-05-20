from pydantic import BaseModel

class MahasiswaRequest(BaseModel):
    nim: str
    nama: str
    jurusan: str
    semester: int