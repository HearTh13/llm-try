from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.llm_service import generate_response_async
from app.auth_utils import get_optional_user

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat_with_gemini(request: ChatRequest, user: dict = Depends(get_optional_user)):
    # Jika yang login adalah mahasiswa, ambil NIM-nya untuk dibawa ke LLM
    # sehingga "SKS saya" otomatis merujuk ke dirinya (dan tidak bisa lihat NIM lain).
    student_nim = None
    if user and user.get("role") == "mahasiswa":
        student_nim = user.get("nim")

    response_text = await generate_response_async(request.prompt, student_nim=student_nim)
    return {"prompt": request.prompt, "response": response_text}