from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base
import uuid
import datetime

class TLLMProfile(Base):
    __tablename__ = "tllm_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False) # openai, anthropic, ollama, custom
    endpoint_url = Column(String, nullable=True)
    api_key_ref = Column(String, nullable=True)
    system_prompt = Column(String, nullable=True)
    has_rag = Column(Boolean, default=False)
    accepts_documents = Column(Boolean, default=False)
    accepts_multimodal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
