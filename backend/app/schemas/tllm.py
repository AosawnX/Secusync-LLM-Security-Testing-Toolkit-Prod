from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TLLMProfileBase(BaseModel):
    name: str = Field(..., description="Name of the profile")
    provider: str = Field(..., description="Provider type (openai, anthropic, ollama, custom)")
    endpoint_url: Optional[str] = Field(None, description="Endpoint URL if applicable")
    api_key_ref: Optional[str] = Field(None, description="API Key reference or actual key")
    system_prompt: Optional[str] = Field(None, description="System prompt to initialize the model with, if any")
    has_rag: bool = Field(False, description="Does it use RAG?")
    accepts_documents: bool = Field(False, description="Does it accept document uploads?")
    accepts_multimodal: bool = Field(False, description="Does it accept multimodal input?")

class TLLMProfileCreate(TLLMProfileBase):
    pass

class TLLMProfileResponse(TLLMProfileBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
