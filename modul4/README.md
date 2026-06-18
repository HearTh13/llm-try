# Modul 4: AI Virtual Assistant Akademik + RAG

Modul ini melanjutkan Modul 3 (FastAPI + Database + LLM Function Calling) dengan menambahkan
**RAG (Retrieval-Augmented Generation)**. Dengan RAG, asisten dapat menjawab pertanyaan seputar
**kebijakan/ketentuan kampus** (UKT, KKN, aturan SKS) yang isinya berupa teks/dokumen — bukan data
terstruktur di tabel database.

## Konsep: Function Calling vs RAG

Modul 4 memakai pendekatan **hibrida**:

- **Function Calling (warisan Modul 3)** -> untuk data **terstruktur** mahasiswa (NIM, KRS, nilai, IPK).
  LLM menulis query `SELECT` dan menjalankannya lewat tool `execute_academic_query`.
- **RAG (baru di Modul 4)** -> untuk pengetahuan **tidak terstruktur** (dokumen kebijakan).
  Pertanyaan user di-cari kemiripannya ke potongan dokumen, lalu potongan paling relevan
  disuntikkan sebagai konteks ke LLM.

## Komponen Baru

| File | Fungsi |
|------|--------|
| `app/data/knowledge_base/*.md` | Dokumen sumber (UKT, KKN, SKS). **Berlabel DUMMY** — ganti dengan dokumen resmi. |
| `app/models/rag_document.py` | Tabel `rag_chunks` (kolom `embedding` bertipe `vector(768)` dari pgvector). |
| `app/services/embedding_service.py` | Membuat vektor embedding via Gemini `text-embedding-004`. |
| `app/services/rag_service.py` | Ingest dokumen + pencarian similarity (cosine distance). |
| `app/api/rag_routes.py` | Endpoint `POST /api/v1/rag/ingest` dan `GET /api/v1/rag/search`. |
| `app/services/llm_service.py` | Disisipi `build_system_instruction()` yang menyuntikkan konteks RAG. |

## Alur RAG (Pipeline)

1. **Ingest (sekali, atau saat dokumen berubah):**
   `dokumen .md` -> dipecah jadi *chunk* -> tiap chunk di-*embed* (768 dimensi) -> disimpan ke tabel `rag_chunks`.
2. **Query (tiap chat):**
   pertanyaan user di-*embed* -> dicari 4 chunk dengan *cosine distance* terkecil di pgvector ->
   chunk tersebut disuntik ke *system instruction* -> Gemini menjawab berbasis konteks itu.

## Prasyarat

- Database memakai image **`pgvector/pgvector:pg15`** (sudah diatur di `docker-compose.yml` root). Image ini
  adalah Postgres biasa + extension `vector`, jadi tetap kompatibel dengan Modul 1-3.
- `GEMINI_API_KEY` valid di `llm-try/.env` (dipakai untuk LLM **dan** embedding).

## Cara Menjalankan

Dari folder root `llm-try/`:

```bash
docker-compose up --build -d db modul4_rag
```

Service jalan di `http://localhost:8003`. Buka Swagger di `http://localhost:8003/docs`.

### Langkah Wajib: Ingest Knowledge Base

Saat pertama kali (dan setiap kali isi `knowledge_base/` diubah), jalankan indexing:

```bash
curl -X POST http://localhost:8003/api/v1/rag/ingest
```

Atau lewat Swagger: jalankan `POST /api/v1/rag/ingest`. Respon sukses berisi jumlah chunk per file.

## Pengujian

1. **Cek retrieval (debug):**
   `GET /api/v1/rag/search?q=berapa maksimal sks kalau ips saya 3 koma`
   Harus mengembalikan chunk dari `akademik_sks.md` dengan `distance` kecil.

2. **Pertanyaan kebijakan (RAG):**
   `POST /api/v1/chat` body: `{ "prompt": "Apa saja syarat untuk ikut KKN?" }`
   Jawaban diambil dari dokumen KKN.

3. **Pertanyaan data mahasiswa (Function Calling):**
   `{ "prompt": "Berapa IPK mahasiswa NIM 225314001?" }`
   LLM tetap menjalankan query SQL seperti Modul 3.

4. **Pertanyaan gabungan:**
   `{ "prompt": "IPS terakhir NIM 225314001 berapa, dan maksimal SKS yang boleh diambil semester depan?" }`
   Menggabungkan data DB (IPS) + aturan dokumen (batas SKS).

## Catatan Penting

- Dokumen di `knowledge_base/` adalah **CONTOH/DUMMY**, bukan kebijakan resmi USD. Ganti isinya
  dengan dokumen resmi sebelum dipakai sungguhan.
- `GEMINI_API_KEY` yang ada di repo sebaiknya **di-regenerate** karena sudah tersebar.
- Jika menambah dokumen baru, ulangi langkah ingest.
