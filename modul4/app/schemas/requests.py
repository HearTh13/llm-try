from typing import Optional
from pydantic import BaseModel


class MahasiswaRequest(BaseModel):
    nim: str
    nama: str
    jurusan: str
    semester: int


class MataKuliahRequest(BaseModel):
    kode_mk: str
    nama_mk: str
    sks: int
    prodi_id: Optional[int] = None


class KrsRequest(BaseModel):
    mahasiswa_id: int
    mata_kuliah_id: int
    semester_diambil: int
    # Kosongkan (null) jika mata kuliah belum dinilai. Isi 'A'/'B'/'C'/'D'/'E' jika sudah.
    nilai_huruf: Optional[str] = None
