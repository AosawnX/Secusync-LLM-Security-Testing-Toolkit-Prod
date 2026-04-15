from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ScanRunCreate(BaseModel):
    tllm_profile_id: str = Field(..., description="The ID of the target LLM Profile")
    attack_classes: List[str] = Field(..., description="List of attack classes (e.g. ['prompt_injection'])")
    mutation_strategies: List[str] = Field(default=["none"], description="List of mutation strategies to apply")
    mutation_depth: int = Field(default=1, description="Depth of mutation applying")

class ScanRunResponse(BaseModel):
    id: str
    tllm_profile_id: str
    status: str
    attack_classes: str
    mutation_strategies: str
    mutation_depth: int
    total_prompts_sent: int
    vulnerabilities_found: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PromptVariantResponse(BaseModel):
    id: str
    scan_run_id: str
    parent_id: Optional[str]
    attack_class: str
    strategy_applied: Optional[str]
    depth: int
    prompt_text: str
    response_text: Optional[str]
    verdict: str
    deterministic_matches: Optional[str]
    semantic_classification: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
