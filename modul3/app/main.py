from fastapi import FastAPI
from app.api.chat_routes import router as chat_router
from app.database import Base, engine, SessionLocal
from app.models import Mahasiswa, MataKuliah, KRS

# Create tables
Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    try:
        # Check if empty
        if db.query(Mahasiswa).first() is None:
            # Seed Mahasiswa
            m1 = Mahasiswa(nim="111", nama="Budi Santoso", jurusan="Informatika", semester=5)
            m2 = Mahasiswa(nim="222", nama="Siti Aminah", jurusan="Sistem Informasi", semester=3)
            db.add_all([m1, m2])
            
            # Seed MataKuliah
            mk1 = MataKuliah(kode_mk="IF101", nama_mk="Algoritma", sks=3)
            mk2 = MataKuliah(kode_mk="IF102", nama_mk="Basis Data", sks=4)
            db.add_all([mk1, mk2])
            db.commit()
            
            # Seed KRS (after commit so we have IDs)
            db.refresh(m1)
            db.refresh(m2)
            db.refresh(mk1)
            db.refresh(mk2)
            
            krs1 = KRS(mahasiswa_id=m1.id, mata_kuliah_id=mk1.id, semester=5, nilai_huruf="A")
            krs2 = KRS(mahasiswa_id=m1.id, mata_kuliah_id=mk2.id, semester=5, nilai_huruf="B")
            krs3 = KRS(mahasiswa_id=m2.id, mata_kuliah_id=mk1.id, semester=3, nilai_huruf="A")
            db.add_all([krs1, krs2, krs3])
            db.commit()
    finally:
        db.close()

seed_db()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Virtual Assistant API (Modul 3)",
    description="Microservice AI Assistant terintegrasi Database dengan Function Calling",
    version="1.0.0"
)

# Konfigurasi CORS agar frontend (localhost:5173) bisa melakukan fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1", tags=["AI Assistant"])

@app.get("/")
def root():
    return {
        "message": "Virtual Assistant API berjalan normal di Modul 3"
    }