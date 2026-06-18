"""
Konfigurasi provider model (terpusat) agar mudah pindah Gemini <-> Ollama.
Semua dibaca dari environment variable; default = Gemini (perilaku lama).
"""
import os

# Provider untuk LLM chat: "gemini" | "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

# Provider untuk embedding: ikut LLM_PROVIDER bila tidak diset terpisah
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", LLM_PROVIDER).lower().strip()

# Nama model (default disesuaikan per provider)
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gemini-2.5-flash" if LLM_PROVIDER == "gemini" else "qwen3:8b",
).strip()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001" if EMBEDDING_PROVIDER == "gemini" else "nomic-embed-text",
).strip()

# Dimensi vektor embedding. WAJIB sesuai model:
#   gemini-embedding-001 -> 768 (kita set), nomic-embed-text -> 768, bge-m3 -> 1024
# Mengubah nilai ini WAJIB diikuti reset tabel rag_chunks + re-ingest.
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))

# Endpoint Ollama. Dari dalam container Docker, host diakses via host.docker.internal.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")

# Kunci Gemini (dipakai bila provider gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY"))
