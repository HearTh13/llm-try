"""
Service inti RAG (Retrieval-Augmented Generation).

Alur:
1. ensure_vector_extension() -> pastikan extension 'vector' aktif di PostgreSQL.
2. ingest_knowledge_base()   -> baca file markdown, pecah jadi chunk, embed, simpan ke tabel rag_chunks.
3. retrieve_context()        -> embed pertanyaan, cari chunk paling mirip (cosine distance), kembalikan teksnya.
"""
import os
from typing import List, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.rag_document import RagChunk
from app.services import embedding_service

# Folder berisi dokumen sumber knowledge base
KB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base")


def ensure_vector_extension():
    """Aktifkan extension pgvector. Dijalankan sekali saat startup sebelum create_all."""
    db = SessionLocal()
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
    finally:
        db.close()


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def _extract_text(path: str) -> str:
    """
    Ambil teks mentah dari dokumen sesuai ekstensinya.
    Didukung: .md/.txt (teks), .pdf (pypdf), .docx (python-docx).
    PDF hasil scan/gambar akan menghasilkan teks kosong (perlu OCR, belum didukung).
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".md", ".txt"):
        return _read_text_file(path)
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            return ""
    if ext == ".docx":
        try:
            import docx
            d = docx.Document(path)
            return "\n\n".join(p.text for p in d.paragraphs if p.text and p.text.strip())
        except Exception:
            return ""
    return ""


def _split_long(block: str, max_chars: int) -> List[str]:
    """Pecah blok teks panjang menjadi potongan <= max_chars, usahakan di batas spasi."""
    out: List[str] = []
    s = block.strip()
    while len(s) > max_chars:
        cut = s.rfind(" ", 0, max_chars)
        if cut <= 0:
            cut = max_chars
        out.append(s[:cut].strip())
        s = s[cut:].strip()
    if s:
        out.append(s)
    return out


def _chunk_text(raw: str, max_chars: int = 600) -> List[str]:
    """
    Pisah teks jadi chunk: per paragraf (baris kosong), lewati baris catatan
    blockquote, pecah paragraf yang terlalu panjang, lalu gabung paragraf kecil
    sampai mendekati max_chars.
    """
    blocks = [p.strip() for p in raw.split("\n\n")]
    blocks = [p for p in blocks if p and not p.startswith(">")]

    # Pecah dulu blok yang melebihi batas (penting untuk teks PDF tanpa baris kosong)
    paragraphs: List[str] = []
    for b in blocks:
        if len(b) > max_chars:
            paragraphs.extend(_split_long(b, max_chars))
        else:
            paragraphs.append(b)

    chunks: List[str] = []
    buffer = ""
    for p in paragraphs:
        if not buffer:
            buffer = p
        elif len(buffer) + len(p) + 2 <= max_chars:
            buffer += "\n\n" + p
        else:
            chunks.append(buffer)
            buffer = p
    if buffer:
        chunks.append(buffer)
    return chunks


def ingest_knowledge_base() -> dict:
    """
    (Re)indeks seluruh dokumen di KB_DIR ke tabel rag_chunks.
    Tabel dikosongkan dulu agar idempotent (aman dipanggil berulang).
    """
    if not os.path.isdir(KB_DIR):
        return {"status": "error", "message": f"Folder knowledge base tidak ditemukan: {KB_DIR}"}

    files = sorted(f for f in os.listdir(KB_DIR) if f.lower().endswith(ALLOWED_EXT))
    if not files:
        return {"status": "error", "message": "Tidak ada dokumen yang didukung di knowledge base."}

    db: Session = SessionLocal()
    total_chunks = 0
    per_file = {}
    try:
        # Kosongkan index lama
        db.query(RagChunk).delete()
        db.commit()

        for fname in files:
            path = os.path.join(KB_DIR, fname)
            raw = _extract_text(path)

            chunks = _chunk_text(raw)
            if not chunks:
                per_file[fname] = 0
                continue

            # Embed semua chunk file ini sekaligus (batch)
            vectors = embedding_service.embed_documents(chunks)

            rows = [
                RagChunk(source=fname, chunk_index=i, content=chunk, embedding=vec)
                for i, (chunk, vec) in enumerate(zip(chunks, vectors))
            ]
            db.add_all(rows)
            db.commit()

            per_file[fname] = len(rows)
            total_chunks += len(rows)

        return {"status": "ok", "total_chunks": total_chunks, "per_file": per_file}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def retrieve_context(query: str, k: int = 4) -> List[Tuple[str, str, float]]:
    """
    Kembalikan k chunk paling relevan terhadap query.
    Hasil: list of (source, content, distance). distance kecil = lebih mirip.
    """
    try:
        q_vec = embedding_service.embed_query(query)
    except Exception:
        return []

    db: Session = SessionLocal()
    try:
        results = (
            db.query(
                RagChunk.source,
                RagChunk.content,
                RagChunk.embedding.cosine_distance(q_vec).label("distance"),
            )
            .order_by("distance")
            .limit(k)
            .all()
        )
        return [(r.source, r.content, float(r.distance)) for r in results]
    except Exception:
        return []
    finally:
        db.close()


def build_context_block(query: str, k: int = 4) -> str:
    """
    Bangun blok teks konteks siap-suntik ke system instruction LLM.
    String kosong jika tidak ada hasil (mis. index belum di-ingest).
    """
    hits = retrieve_context(query, k=k)
    if not hits:
        return ""

    parts = []
    for source, content, _dist in hits:
        parts.append(f"[Sumber: {source}]\n{content}")
    return "\n\n---\n\n".join(parts)


# ----------------------------------------------------------------------------
# Manajemen dokumen (untuk tab "RAG Documents" di frontend)
# ----------------------------------------------------------------------------

ALLOWED_EXT = (".md", ".txt", ".pdf", ".docx")


def _doc_meta(path: str):
    """Ambil judul + ringkasan singkat sebuah dokumen (untuk ditampilkan di UI)."""
    ext = os.path.splitext(path)[1].lower()
    title = None
    about = None
    try:
        if ext in (".md", ".txt"):
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    s = line.strip()
                    if not s:
                        continue
                    if s.startswith(">"):  # lewati baris catatan blockquote
                        continue
                    if s.startswith("#"):
                        if title is None:
                            title = s.lstrip("#").strip()
                        continue
                    if about is None:
                        about = s[:200]
                    if title and about:
                        break
        else:
            # PDF / DOCX: tidak ada heading markdown, pakai cuplikan teks awal
            text_all = _extract_text(path).strip()
            about = text_all[:200] if text_all else None
    except Exception:
        pass
    return title, about


def _chunk_counts() -> dict:
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT source, COUNT(*) FROM rag_chunks GROUP BY source")
        ).all()
        return {r[0]: int(r[1]) for r in rows}
    except Exception:
        return {}
    finally:
        db.close()


def list_documents() -> dict:
    """Daftar dokumen di knowledge base + ringkasan isi + jumlah chunk ter-index."""
    counts = _chunk_counts()
    docs = []
    if os.path.isdir(KB_DIR):
        for fname in sorted(os.listdir(KB_DIR)):
            if not fname.lower().endswith(ALLOWED_EXT):
                continue
            title, about = _doc_meta(os.path.join(KB_DIR, fname))
            docs.append({
                "filename": fname,
                "title": title or fname,
                "about": about or "(tidak ada ringkasan)",
                "chunks": counts.get(fname, 0),
                "indexed": counts.get(fname, 0) > 0,
            })
    return {"documents": docs, "total": len(docs)}


def save_uploaded_document(filename: str, content: bytes) -> dict:
    """Simpan dokumen yang di-upload ke folder knowledge base (.md/.txt/.pdf/.docx)."""
    safe_name = os.path.basename(filename or "").strip()
    if not safe_name:
        return {"status": "error", "message": "Nama file tidak valid."}
    if not safe_name.lower().endswith(ALLOWED_EXT):
        return {"status": "error", "message": "Format tidak didukung. Hanya .md, .txt, .pdf, .docx."}

    os.makedirs(KB_DIR, exist_ok=True)
    # Tulis biner agar mendukung PDF/DOCX; .md/.txt pun aman ditulis sebagai byte.
    with open(os.path.join(KB_DIR, safe_name), "wb") as fh:
        fh.write(content)
    return {"status": "ok", "filename": safe_name}


def delete_document(filename: str) -> dict:
    """Hapus satu dokumen dari knowledge base."""
    safe_name = os.path.basename(filename or "").strip()
    path = os.path.join(KB_DIR, safe_name)
    if not safe_name or not os.path.isfile(path):
        return {"status": "error", "message": "Dokumen tidak ditemukan."}
    os.remove(path)
    return {"status": "ok", "filename": safe_name}
