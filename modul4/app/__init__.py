# Muat file .env (jika ada) saat menjalankan TANPA Docker.
# Aman diabaikan saat di Docker (env sudah disuntik compose).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
