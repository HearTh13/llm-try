from fastapi import FastAPI

app = FastAPI(
    title="FastAPI CRUD API",
    description="API sederhana untuk mengelola data mahasiswa, mata kuliah, KRS, dan nilai",
    version="1.0.0"
)

app.include_router(mahasiswa_router)


@app.get("/")
def root():
    return {
        "message": "FastAPI CRUD API berhasil dijalankan"
    }