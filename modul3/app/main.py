from fastapi import FastAPI
from app.api.chat_routes import router as chat_router
from app.database import Base, engine, SessionLocal
from app.models import Mahasiswa, MataKuliah, KRS, Fakultas, Prodi

# Create tables
Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    try:
        if db.query(Fakultas).first() is None:
            # Seed Fakultas
            fst = Fakultas(singkatan="FST", nama="Fakultas Sains dan Teknologi")
            fkip = Fakultas(singkatan="FKIP", nama="Fakultas Keguruan dan Ilmu Pendidikan")
            fekon = Fakultas(singkatan="FE", nama="Fakultas Ekonomi")
            db.add_all([fst, fkip, fekon])
            db.commit()
            db.refresh(fst)
            db.refresh(fkip)
            
            # Seed Prodi
            p_if = Prodi(fakultas_id=fst.id, nama="Informatika", jenjang="S1")
            p_mt = Prodi(fakultas_id=fst.id, nama="Matematika", jenjang="S1")
            p_te = Prodi(fakultas_id=fst.id, nama="Teknik Elektro", jenjang="S1")
            p_pgsd = Prodi(fakultas_id=fkip.id, nama="Pendidikan Guru Sekolah Dasar", jenjang="S1")
            db.add_all([p_if, p_mt, p_te, p_pgsd])
            db.commit()
            db.refresh(p_if)
            
            # Seed Mahasiswa Dummy USD (NIM 225314001, Angkatan 2022, Smt 6)
            m1 = Mahasiswa(nim="225314001", nama="Budi Santoso", jurusan="Informatika", semester=6)
            db.add(m1)
            db.commit()
            db.refresh(m1)
            
            # Seed MataKuliah Informatika & Historical KRS programmatically (Semester 1 to 5)
            import random
            random.seed(42) # For reproducible results
            
            krs_hist = []
            for smt in range(1, 6): # Semesters 1 to 5
                for i in range(7): # 7 classes per semester
                    sks = 3
                    mk = MataKuliah(kode_mk=f"IF{smt}0{i+1}", nama_mk=f"Mata Kuliah Dummy {smt}-{i+1}", sks=sks, prodi_id=p_if.id)
                    db.add(mk)
                    db.commit()
                    db.refresh(mk)
                    
                    # Random grade weighted towards A and B
                    grade = random.choice(["A", "A", "B", "B", "B", "C", "C"])
                    krs = KRS(mahasiswa_id=m1.id, mata_kuliah_id=mk.id, semester_diambil=smt, nilai_huruf=grade)
                    krs_hist.append(krs)
                    
            db.add_all(krs_hist)
            db.commit()
            
            # Seed explicit courses for Semester 6 (Current)
            mk5 = MataKuliah(kode_mk="IF601", nama_mk="Kerja Praktek", sks=2, prodi_id=p_if.id)
            mk6 = MataKuliah(kode_mk="IF602", nama_mk="Pemrograman Web", sks=3, prodi_id=p_if.id)
            db.add_all([mk5, mk6])
            db.commit()
            db.refresh(mk5); db.refresh(mk6)
            
            krs_curr = [
                KRS(mahasiswa_id=m1.id, mata_kuliah_id=mk5.id, semester_diambil=6, nilai_huruf=None),
                KRS(mahasiswa_id=m1.id, mata_kuliah_id=mk6.id, semester_diambil=6, nilai_huruf=None)
            ]
            db.add_all(krs_curr)
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