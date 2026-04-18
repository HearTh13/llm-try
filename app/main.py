from fastapi import FastAPI
from app.core import database
from app.models.chat import ChatHistory
from app.models.product import Product
from app.models.faculty import Faculty
from app.models.study_program import StudyProgram
from app.models.building import Building
from app.models.news import News
# ------------------------------
from app.api import chat_routes, product_routes, faculty_routes, study_program_routes, news_routes, building_routes

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Ecommerce & AI - Project 1 & 2")

app.include_router(chat_routes.router, prefix="/chat", tags=["AI Chat"])
app.include_router(product_routes.router, prefix="/products", tags=["Ecommerce"])
app.include_router(faculty_routes.router, prefix="/faculties", tags=["University"])
app.include_router(study_program_routes.router, prefix="/study-programs", tags=["University"])
app.include_router(building_routes.router, prefix="/buildings", tags=["University"])
app.include_router(news_routes.router, prefix="/news", tags=["University"])

@app.get("/")
def home():
    return {"message": "Selamat datang di API Ecommerce & AI!"}