from fastapi import FastAPI
from app.api.chat_routes import router as chat_router

app = FastAPI(
    title="LLM Gemini Service API",
    description="Microservice khusus untuk menangani interaksi dengan Google Gemini LLM",
    version="1.0.0"
)

app.include_router(chat_router, prefix="/api/v1", tags=["LLM Gemini"])

@app.get("/")
def root():
    return {
        "message": "LLM Service API berjalan normal di Modul 2"
    }