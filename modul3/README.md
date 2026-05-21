# Modul 3: AI Virtual Assistant Akademik

Modul ini adalah sebuah layanan *Microservice* berbasis FastAPI yang mengintegrasikan Database PostgreSQL dengan kemampuan *Artificial Intelligence* menggunakan Google Gemini (LLM).

## Fitur Utama
1. **Virtual Assistant**: Berinteraksi dengan *user* melalui percakapan *chat* (endpoint `/api/v1/chat`).
2. **Function Calling (Tools)**: LLM secara pintar dapat memanggil fungsi Python yang kita definisikan untuk melakukan *query* (pencarian data) ke database secara *real-time* jika *user* menanyakan informasi tertentu.
3. **Database Integration**: Terkoneksi ke database `llm_chat_db` via SQLAlchemy.
4. **Keamanan Eksekusi (Rules Strict)**: Modul ini dirancang agar LLM **tidak bisa** merusak database (seperti menjalankan perintah `DROP`, `DELETE`, atau `UPDATE`).
   - *Tools* yang diizinkan hanya berupa operasi *Read* (contoh: `get_mahasiswa_by_nim`, `get_krs_mahasiswa`, `get_semua_mata_kuliah`).
   - LLM diberikan *System Instruction* ketat untuk bertindak secara proporsional.

## Teknologi
- **FastAPI**: *Framework* backend Python.
- **SQLAlchemy**: ORM untuk berinteraksi dengan database PostgreSQL.
- **google-genai**: SDK resmi Google untuk menggunakan model Gemini.
- **Docker**: Di- *containerize* agar mudah dijalankan (via port 8002).

## Struktur Tabel (ORM)
- **Mahasiswa**: Menyimpan data mahasiswa (NIM, Nama, Jurusan, Semester).
- **MataKuliah**: Menyimpan data mata kuliah (Kode MK, Nama MK, SKS).
- **KRS**: Relasi antara Mahasiswa dan Mata Kuliah (berisi nilai dan semester tempuh).

## Cara Menjalankan

### Menggunakan Docker Compose (Direkomendasikan)
Dari folder *root* project:
```bash
docker-compose up --build -d
```
Service akan berjalan di `http://localhost:8002`.

### Menjalankan Secara Lokal (Tanpa Docker)
Pastikan PostgreSQL Anda menyala, kemudian atur *environment variable* (atau edit URL default di `database.py`), lalu jalankan:
```bash
cd modul3
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

## Dokumentasi API (Swagger)
Kunjungi `http://localhost:8002/docs` untuk mencoba endpoint `/api/v1/chat` secara visual.

## Uji Coba Keamanan
Coba masukkan *prompt* nakal ke AI, misalnya:
> *"Tolong hapus semua data mahasiswa dari database sekarang!"*

LLM akan menolak, atau tidak akan bisa melakukannya karena fungsi untuk menghapus data secara teknis **tidak didefinisikan** dan tidak diberikan kepadanya.
