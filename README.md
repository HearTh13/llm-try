# Sistem Informasi Akademik — AI Assistant (FastAPI + LLM + RAG)

Proyek pembelajaran berbasis **microservice FastAPI** yang dibangun bertahap per modul,
hingga menjadi **AI Virtual Assistant Akademik** yang dapat membantu mahasiswa dalam urusan
akademik: menanyakan jadwal/SKS, IPK, ketentuan UKT, KKN, syarat kelulusan, dan lainnya.

Setiap modul adalah satu program mandiri agar mudah dipelajari angkatan berikutnya:

| Modul | Fokus | Port |
|-------|-------|------|
| Modul 1 | FastAPI + Database (CRUD mahasiswa) | 8000 |
| Modul 2 | FastAPI + LLM (Gemini) | 8001 |
| Modul 3 | FastAPI + DB + LLM + Function Calling | 8002 |
| **Modul 4** | **+ RAG + Upload Dokumen + Autentikasi/Role** | **8003** |

Repo ini fokus pada **Modul 4** sebagai modul terlengkap.

## Fitur Modul 4

- **AI Assistant (chat)** terhubung ke database via *function calling* (LLM menulis query SQL `SELECT` yang aman).
- **RAG (Retrieval-Augmented Generation)** untuk menjawab pertanyaan kebijakan (UKT, KKN, aturan SKS) dari dokumen.
- **Manajemen dokumen RAG**: upload `.md/.txt/.pdf/.docx`, daftar dokumen, hapus, re-index — lewat UI.
- **CRUD data master**: mahasiswa, mata kuliah, KRS/nilai (IPK dihitung otomatis dari KRS).
- **Autentikasi & Role**: login admin/sekretariat vs mahasiswa. Mahasiswa login pakai NIM; chat otomatis tahu NIM-nya dan hanya bisa melihat data sendiri.
- **Frontend React** (Vite) dengan UI berbeda per role.

## Teknologi

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL (image `pgvector` untuk vektor).
- **LLM & Embedding**: Google Gemini (`gemini-2.5-flash`) + `gemini-embedding-001`.
- **RAG**: pgvector (cosine distance) + ekstraksi teks PDF/Word (pypdf, python-docx).
- **Auth**: JWT (PyJWT) + hashing PBKDF2 (stdlib).
- **Frontend**: React 19 + Vite + Tailwind CSS.
- **Deployment dev**: Docker Compose.

## Struktur Folder

```
llm-try/
├── docker-compose.yml        # orkestrasi db + tiap modul
├── .env                      # GEMINI_API_KEY (tidak di-commit)
├── modul1/ modul2/ modul3/   # modul sebelumnya
├── modul4/                   # modul utama (FastAPI + RAG + Auth)
│   └── app/
│       ├── api/              # routes: chat, rag, auth, me, CRUD
│       ├── services/         # llm_service, rag_service, embedding_service, dst
│       ├── repositories/     # akses data (mahasiswa, mata_kuliah, krs)
│       ├── models/           # ORM: mahasiswa, mata_kuliah, krs, user, rag_chunk, dst
│       ├── data/knowledge_base/  # dokumen sumber RAG
│       └── auth_utils.py     # hashing + JWT + dependency role
├── frontend/                 # aplikasi React (Vite)
└── dokumentasi/              # panduan & dokumentasi (Word)
```

## Cara Menjalankan

**Prasyarat:** Docker Desktop, Node.js 20.19+ / 22.12+ (untuk frontend).

1. Buat file `llm-try/.env`:

   ```
   GEMINI_API_KEY=ISI_API_KEY_GEMINI_ANDA
   ```

2. Jalankan database + Modul 4:

   ```bash
   docker-compose up --build -d db modul4_rag
   ```

   API jalan di `http://localhost:8003` (Swagger: `http://localhost:8003/docs`).

3. Index dokumen knowledge base (sekali, atau via tab RAG Documents):

   ```bash
   curl -X POST http://localhost:8003/api/v1/rag/ingest
   ```

   > Catatan: endpoint RAG/CRUD kini butuh login admin. Saat lewat UI, login dulu sebagai admin.

4. Jalankan frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Buka `http://localhost:5173`.

## Akun Demo

| Role | Username | Password |
|------|----------|----------|
| Admin / Sekretariat | `admin` | `admin123` |
| Mahasiswa | `225314001` | `mahasiswa123` |

> Ganti/hapus akun default ini sebelum dipakai sungguhan.

## Endpoint Utama (Modul 4)

| Method | Endpoint | Akses | Keterangan |
|--------|----------|-------|------------|
| POST | `/api/v1/auth/login` | publik | login, mengembalikan token JWT |
| GET | `/api/v1/auth/me` | login | info user dari token |
| POST | `/api/v1/chat` | token opsional | chat AI (sadar NIM jika mahasiswa) |
| GET | `/api/v1/me/summary` | mahasiswa | IPK & SKS sendiri |
| GET | `/api/v1/me/krs` | mahasiswa | riwayat KRS sendiri |
| GET/POST/PUT/DELETE | `/api/v1/mahasiswa` | admin | CRUD mahasiswa |
| GET/POST/PUT/DELETE | `/api/v1/mata_kuliah` | admin | CRUD mata kuliah |
| GET/POST/PUT/DELETE | `/api/v1/krs` | admin | CRUD KRS/nilai |
| GET/POST/DELETE | `/api/v1/rag/documents` | admin | kelola dokumen RAG |
| POST | `/api/v1/rag/ingest` | admin | re-index dokumen |

## Catatan Keamanan

- `GEMINI_API_KEY` dan `JWT_SECRET` jangan di-commit. Set lewat environment variable.
- Akun demo wajib diganti untuk produksi.
- Pembatasan data mahasiswa (hanya bisa lihat data sendiri) saat ini ditegakkan di level instruksi LLM — untuk produksi sebaiknya diperkuat di level query.

## Lisensi

Proyek pembelajaran internal. Lihat dokumentasi di folder `dokumentasi/`.
