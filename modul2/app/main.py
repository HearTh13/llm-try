from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat_routes import router as chat_router
from app.api.mahasiswa_routes import router as mahasiswa_router
from app.database import Base, engine
from app.models.mahasiswa import Mahasiswa

app = FastAPI(
    title="LLM Gemini Service API",
    description="Microservice khusus untuk menangani interaksi dengan Google Gemini LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Atau sebutkan spesifik origin frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1", tags=["LLM Gemini"])
app.include_router(mahasiswa_router, prefix="/api/v1", tags=["Mahasiswa"])

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "message": "LLM Service API berjalan normal di Modul 2"
    }