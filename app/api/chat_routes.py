from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.chat import ChatHistory
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import tanya_ai_dengan_konteks
from app.services.agent_service import tanya_ai_dengan_agent

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ask", response_model=ChatResponse)
def proses_obrolan_ai(request: ChatRequest, db: Session = Depends(get_db)):
    jawaban = tanya_ai_dengan_konteks(request.prompt, db)
    
    history_baru = ChatHistory(user_prompt=request.prompt, llm_response=jawaban)
    db.add(history_baru)
    db.commit()
    
    return ChatResponse(prompt=request.prompt, jawaban_ai=jawaban)

@router.post("/ask-agent", response_model=ChatResponse)
def proses_obrolan_ai(request: ChatRequest, db: Session = Depends(get_db)):
    jawaban = tanya_ai_dengan_agent(request.prompt, db)
    
    history_baru = ChatHistory(user_prompt=request.prompt, llm_response=jawaban)
    db.add(history_baru)
    db.commit()
    
    return ChatResponse(prompt=request.prompt, jawaban_ai=jawaban)
