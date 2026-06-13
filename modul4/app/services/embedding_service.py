"""
Service untuk membuat vektor embedding dari teks menggunakan Google Gemini.
Model: text-embedding-004 (dimensi 768).

Penting soal task_type:
- RETRIEVAL_DOCUMENT  -> dipakai saat meng-embed dokumen/chunk yang akan disimpan.
- RETRIEVAL_QUERY     -> dipakai saat meng-embed pertanyaan user untuk pencarian.
Memakai task_type yang tepat meningkatkan kualitas hasil pencarian.
"""
import os
from typing import List
from google import genai
from google.genai import types

# text-embedding-004 dideprecate Google 14 Jan 2026 -> ganti ke gemini-embedding-001.
# gemini-embedding-001 default 3072 dim, tapi mendukung MRL untuk diturunkan ke 768.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001").strip()
EMBEDDING_DIM = 768

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY"))

_client = None
if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("GANTI"):
    _client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


def _embed(texts: List[str], task_type: str) -> List[List[float]]:
    if _client is None:
        raise RuntimeError("GEMINI_API_KEY belum di-setup, tidak bisa membuat embedding.")

    resp = _client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    return [list(e.values) for e in resp.embeddings]


def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embed banyak chunk dokumen (untuk disimpan ke vector store)."""
    if not texts:
        return []
    return _embed(texts, task_type="RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> List[float]:
    """Embed satu pertanyaan user (untuk pencarian similarity)."""
    return _embed([text], task_type="RETRIEVAL_QUERY")[0]
