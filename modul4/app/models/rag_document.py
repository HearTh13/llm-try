from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.database import Base
from app import config

# Dimensi vektor mengikuti config (default 768). Ubah lewat EMBEDDING_DIM di .env.
# Catatan: mengubah dimensi WAJIB diikuti reset tabel rag_chunks + re-ingest.
EMBEDDING_DIM = config.EMBEDDING_DIM


class RagChunk(Base):
    """
    Menyimpan potongan (chunk) dokumen kebijakan akademik beserta vektor embedding-nya.
    Dipakai untuk Retrieval-Augmented Generation (RAG): mencari chunk paling relevan
    terhadap pertanyaan user, lalu menyuntikkannya sebagai konteks ke LLM.
    """
    __tablename__ = "rag_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False, index=True)  # nama file sumber, e.g. "ukt.md"
    chunk_index = Column(Integer, nullable=False)              # urutan chunk dalam dokumen
    content = Column(Text, nullable=False)                     # teks asli chunk
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)  # vektor embedding
