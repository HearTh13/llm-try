from fastapi import APIRouter, Query, UploadFile, File
from app.services import rag_service

router = APIRouter()


@router.get("/documents")
def list_documents():
    """Daftar dokumen knowledge base + ringkasan isi + jumlah chunk ter-index."""
    return rag_service.list_documents()


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload dokumen (.md/.txt) ke knowledge base, lalu otomatis re-index semua dokumen.
    """
    content = await file.read()
    saved = rag_service.save_uploaded_document(file.filename, content)
    if saved.get("status") != "ok":
        return saved
    ingest = rag_service.ingest_knowledge_base()
    return {"status": "ok", "uploaded": saved["filename"], "ingest": ingest}


@router.delete("/documents/{filename}")
def delete_document(filename: str):
    """Hapus satu dokumen dari knowledge base, lalu otomatis re-index ulang."""
    deleted = rag_service.delete_document(filename)
    if deleted.get("status") != "ok":
        return deleted
    ingest = rag_service.ingest_knowledge_base()
    return {"status": "ok", "deleted": deleted["filename"], "ingest": ingest}


@router.post("/ingest")
def ingest_knowledge_base():
    """
    (Re)indeks seluruh dokumen knowledge base ke vector store.
    Jalankan endpoint ini sekali setelah service nyala (atau tiap dokumen berubah).
    """
    return rag_service.ingest_knowledge_base()


@router.get("/search")
def search(q: str = Query(..., description="Pertanyaan untuk diuji"), k: int = 4):
    """
    Debugging retrieval: lihat chunk mana yang terambil untuk sebuah pertanyaan,
    beserta jarak (distance) cosine-nya. Berguna untuk mengevaluasi kualitas RAG.
    """
    hits = rag_service.retrieve_context(q, k=k)
    return {
        "query": q,
        "results": [
            {"source": s, "distance": round(d, 4), "content": c}
            for s, c, d in hits
        ],
    }
