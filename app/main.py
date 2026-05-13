from fastapi import FastAPI
from app.api.mahasiswa_routes import router as mahasiswa_router
from app.database import Base, engine
from app.models.mahasiswa import Mahasiswa

app = FastAPI(
    title="FastAPI CRUD API",
    description="API sederhana untuk mengelola data mahasiswa, mata kuliah, KRS, dan nilai",
    version="1.0.0"
)

app.include_router(mahasiswa_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "message": "FastAPI CRUD API berhasil dijalankan"
    }