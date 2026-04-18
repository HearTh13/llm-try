import requests
from sqlalchemy.orm import Session

from app.models.faculty import Faculty
from app.models.study_program import StudyProgram
from app.models.building import Building
from app.models.news import News

OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"

def tanya_ai_dengan_konteks(prompt_user: str, db: Session) -> str:
    # Ambil data dari database
    faculties = db.query(Faculty).all()
    study_programs = db.query(StudyProgram).all()
    buildings = db.query(Building).all()
    news_list = db.query(News).order_by(News.date.desc()).limit(10).all()

    # Fakultas
    faculty_context = "\n".join(
        f"Nama: {f.name}\nDeskripsi: {f.description}"
        for f in faculties
    )

    # Program studi
    program_context = "\n\n".join(
        (
            f"Nama: {p.name}\n"
            f"Jenjang: {p.degree}\n"
            f"Faculty ID: {p.faculty_id}\n"
            f"Akreditasi: {p.accreditation}\n"
            f"Deskripsi: {p.description}"
        )
        for p in study_programs
    )

    # Gedung dan lokasi
    building_context = "\n\n".join(
        (
            f"Kategori: {b.category}\n"
            f"Nama: {b.name}\n"
            f"Alamat: {b.address}\n"
            f"Deskripsi: {b.description}\n"
            f"Latitude: {b.latitude}\n"
            f"Longitude: {b.longitude}"
        )
        for b in buildings
    )

    # Berita
    news_context = "\n\n".join(
        (
            f"Judul: {n.title}\n"
            f"Isi: {n.content}"
        )
        for n in news_list
    )

    context = f"""
        === FAKULTAS ===
        {faculty_context}

        === PROGRAM STUDI ===
        {program_context}

        === GEDUNG DAN LOKASI ===
        {building_context}

        === BERITA ===
        {news_context}
        """

    full_prompt = f"""
        Kamu adalah chatbot informasi kampus.

        Jawab HANYA berdasarkan data yang diberikan.

        ATURAN:
        - Jika user menanyakan perpustakaan, gunakan data dengan kategori "perpustakaan".
        - Jika user menanyakan masjid, gunakan data dengan kategori "ibadah".
        - Jika user menanyakan parkir, gunakan data dengan kategori "parkir".
        - Jika user menanyakan lokasi suatu tempat, jawab nama tempat dan alamatnya.
        - Jangan menyebut "lihat bagian GEDUNG DAN LOKASI".
        - Jangan membuat informasi yang tidak ada.
        - Jika informasi tidak ditemukan atau belum tersedia, jawab:
        "Informasi tersebut belum tersedia di database kampus."

        === Konteks ===
        {context}

        PERTANYAAN USER:
        {prompt_user}

        JAWABAN:
        """

    payload = {
        "model": "llama3.2",
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=180
        )
        response.raise_for_status()

        result = response.json()
        return result.get("response", "AI tidak memberikan jawaban.")

    except Exception as e:
        return f"Kesalahan koneksi AI: {e}"