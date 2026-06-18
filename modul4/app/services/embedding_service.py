"""
Service embedding. Mendukung dua provider:
  - gemini : Google Gemini (text/gemini-embedding) via SDK google-genai.
  - ollama : model lokal (mis. nomic-embed-text, bge-m3) via API OpenAI-compatible.

Pemilihan provider & model lewat app/config.py (environment variable).
"""
from typing import List
from app import config

EMBEDDING_DIM = config.EMBEDDING_DIM

# ----------------------------- Provider: Gemini -----------------------------
_gemini_client = None
if config.EMBEDDING_PROVIDER == "gemini":
    from google import genai
    from google.genai import types as _genai_types
    if config.GEMINI_API_KEY and not config.GEMINI_API_KEY.startswith("GANTI"):
        _gemini_client = genai.Client(
            api_key=config.GEMINI_API_KEY, http_options={"api_version": "v1beta"}
        )

# ----------------------------- Provider: Ollama -----------------------------
_ollama_client = None
def _get_ollama():
    global _ollama_client
    if _ollama_client is None:
        from openai import OpenAI
        _ollama_client = OpenAI(base_url=config.OLLAMA_BASE_URL + "/v1", api_key="ollama")
    return _ollama_client


def _embed_gemini(texts: List[str], task_type: str) -> List[List[float]]:
    if _gemini_client is None:
        raise RuntimeError("GEMINI_API_KEY belum di-setup untuk embedding.")
    resp = _gemini_client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=texts,
        config=_genai_types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=config.EMBEDDING_DIM,
        ),
    )
    return [list(e.values) for e in resp.embeddings]


def _embed_ollama(texts: List[str]) -> List[List[float]]:
    client = _get_ollama()
    resp = client.embeddings.create(model=config.EMBEDDING_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def _embed(texts: List[str], task_type: str) -> List[List[float]]:
    if not texts:
        return []
    if config.EMBEDDING_PROVIDER == "ollama":
        return _embed_ollama(texts)
    return _embed_gemini(texts, task_type)


def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embed banyak chunk dokumen (untuk disimpan ke vector store)."""
    return _embed(texts, task_type="RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> List[float]:
    """Embed satu pertanyaan user (untuk pencarian similarity)."""
    return _embed([text], task_type="RETRIEVAL_QUERY")[0]
