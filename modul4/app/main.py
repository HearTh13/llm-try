from fastapi import FastAPI, Depends
from app.api.chat_routes import router as chat_router
from app.api.rag_routes import router as rag_router
from app.api.mahasiswa_routes import router as mahasiswa_router
from app.api.mata_kuliah_routes import router as mata_kuliah_router
from app.api.krs_routes import router as krs_router
from app.api.auth_routes import router as auth_router
from app.api.me_routes import router as me_router
from app.database import Base, engine, SessionLocal
from app.models import Mahasiswa, MataKuliah, KRS, Fakultas, Prodi, RagChunk
from app.models.user import User
from app.services.rag_service import ensure_vector_extension
from app.auth_utils import require_admin, hash_password

# Aktifkan extension pgvector SEBELUM create_all (tabel rag_chunks butuh tipe vector)
ensure_vector_extension()

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


def seed_users():
    """Buat akun default sekali. Admin + akun mahasiswa untuk Budi (NIM 225314001)."""
    db = SessionLocal()
    try:
        if db.query(User).first() is None:
            db.add(User(username="admin", password_hash=hash_password("admin123"), role="admin"))
            budi = db.query(Mahasiswa).filter(Mahasiswa.nim == "225314001").first()
            if budi:
                db.add(User(
                    username=budi.nim,
                    password_hash=hash_password("mahasiswa123"),
                    role="mahasiswa",
                    mahasiswa_id=budi.id,
                ))
            db.commit()
    finally:
        db.close()

seed_users()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Virtual Assistant API (Modul 4 - RAG)",
    description="Microservice AI Assistant terintegrasi Database dengan Function Calling (basis untuk RAG)",
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

# Publik / semi-publik
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(chat_router, prefix="/api/v1", tags=["AI Assistant"])  # token opsional (sadar NIM)
app.include_router(me_router, prefix="/api/v1/me", tags=["Mahasiswa (Data Saya)"])  # butuh login mahasiswa

# Khusus admin/sekretariat (wajib token role admin)
admin_only = [Depends(require_admin)]
app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"], dependencies=admin_only)
app.include_router(mahasiswa_router, prefix="/api/v1", tags=["Mahasiswa CRUD"], dependencies=admin_only)
app.include_router(mata_kuliah_router, prefix="/api/v1", tags=["Mata Kuliah CRUD"], dependencies=admin_only)
app.include_router(krs_router, prefix="/api/v1", tags=["KRS CRUD"], dependencies=admin_only)

@app.get("/")
def root():
    return {
        "message": "Virtual Assistant API berjalan normal di Modul 4"
    }
