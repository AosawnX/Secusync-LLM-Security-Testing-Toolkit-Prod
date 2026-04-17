from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
import uuid
import datetime

class PromptVariant(Base):
    __tablename__ = "prompt_variants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Denormalised copy of scan_runs.user_id for defence-in-depth — lets the
    # hot read path filter variants by user without an extra JOIN, and makes
    # "forgot one filter" bugs impossible to hide.
    user_id = Column(String, nullable=False, index=True)
    scan_run_id = Column(String, nullable=False)
    parent_id = Column(String, nullable=True)
    attack_class = Column(String, nullable=False)
    strategy_applied = Column(String, nullable=True)
    depth = Column(Integer, default=0)
    prompt_text = Column(String, nullable=False)
    response_text = Column(String, nullable=True)
    verdict = Column(String, nullable=False, default="UNCERTAIN") # VULNERABLE, NOT_VULNERABLE, NEEDS_REVIEW, UNCERTAIN
    deterministic_matches = Column(String, nullable=True) # json representation
    semantic_classification = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
