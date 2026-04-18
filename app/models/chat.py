from sqlalchemy import Column, Integer, Text
from app.core.database import Base # Sekarang import ini akan bekerja

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_prompt = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)