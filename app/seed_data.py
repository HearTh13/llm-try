from app.core.database import SessionLocal, engine
from app.models.faculty import Faculty
from app.models.study_program import StudyProgram
from app.models.building import Building
from app.models.news import News
from app.core.database import Base

def seed():
    db = SessionLocal()
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # 1. Seed Faculties
    if db.query(Faculty).count() == 0:
        faculties = [
            Faculty(name="Fakultas Teknik", description="Fakultas yang berfokus pada inovasi teknologi dan rekayasa."),
            Faculty(name="Fakultas Ekonomi dan Bisnis", description="Fakultas yang mencetak pemimpin bisnis dan ahli ekonomi."),
            Faculty(name="Fakultas Ilmu Komputer", description="Pusat keunggulan di bidang teknologi informasi dan kecerdasan buatan."),
            Faculty(name="Fakultas Hukum", description="Menghasilkan praktisi hukum yang berintegritas."),
        ]
        db.add_all(faculties)
        db.commit()
        print("Faculties seeded.")

    # 2. Seed Study Programs
    if db.query(StudyProgram).count() == 0:
        ft = db.query(Faculty).filter_by(name="Fakultas Teknik").first()
        feb = db.query(Faculty).filter_by(name="Fakultas Ekonomi dan Bisnis").first()
        fik = db.query(Faculty).filter_by(name="Fakultas Ilmu Komputer").first()

        programs = [
            StudyProgram(faculty_id=ft.id, name="Teknik Sipil", degree="S1", accreditation="A"),
            StudyProgram(faculty_id=ft.id, name="Teknik Mesin", degree="S1", accreditation="A"),
            StudyProgram(faculty_id=fik.id, name="Informatika", degree="S1", accreditation="Unggul"),
            StudyProgram(faculty_id=fik.id, name="Sistem Informasi", degree="S1", accreditation="A"),
            StudyProgram(faculty_id=feb.id, name="Manajemen", degree="S1", accreditation="A"),
            StudyProgram(faculty_id=feb.id, name="Akuntansi", degree="S1", accreditation="A"),
        ]
        db.add_all(programs)
        db.commit()
        print("Study programs seeded.")

    # 3. Seed Buildings
    if db.query(Building).count() == 0:
        buildings = [
            Building(name="Gedung Rektorat", category="administrasi", description="Pusat administrasi universitas.", address="Jl. Kampus No. 1", latitude=-6.123, longitude=106.123),
            Building(name="Masjid Kampus Al-Hikmah", category="ibadah", description="Tempat ibadah utama di kampus.", address="Samping Perpustakaan", latitude=-6.124, longitude=106.124),
            Building(name="Perpustakaan Pusat", category="perpustakaan", description="Koleksi buku terlengkap dengan fasilitas ruang baca modern.", address="Zona Utara", latitude=-6.125, longitude=106.125),
            Building(name="Parkir Timur", category="parkir", description="Area parkir luas untuk motor dan mobil.", address="Pintu Timur", latitude=-6.126, longitude=106.126),
            Building(name="Gedung Dekanat Teknik", category="fakultas", description="Kantor pusat Fakultas Teknik.", address="Zona Selatan", latitude=-6.127, longitude=106.127),
        ]
        db.add_all(buildings)
        db.commit()
        print("Buildings seeded.")

    # 4. Seed News
    if db.query(News).count() == 0:
        news = [
            News(title="Pembukaan Expo Teknologi 2026", content="Acara tahunan pameran inovasi mahasiswa teknik akan diadakan bulan depan.", date="2026-04-01"),
            News(title="Prestasi Mahasiswa Informatika", content="Tim robotika universitas berhasil meraih juara 1 di tingkat nasional.", date="2026-04-10"),
            News(title="Pendaftaran Beasiswa Unggulan", content="Telah dibuka pendaftaran beasiswa untuk mahasiswa berprestasi tahun akademik 2026/2027.", date="2026-04-15"),
        ]
        db.add_all(news)
        db.commit()
        print("News seeded.")

    db.close()

if __name__ == "__main__":
    seed()
