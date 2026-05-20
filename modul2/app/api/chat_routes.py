from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_response_async

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat_with_gemini(request: ChatRequest):
    # Panggil fungsi service secara asinkron
    response_text = await generate_response_async(request.prompt)
    return {"prompt": request.prompt, "response": response_text}