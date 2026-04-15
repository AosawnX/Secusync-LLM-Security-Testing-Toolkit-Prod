from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base
import uuid
import datetime

class ScanRun(Base):
    __tablename__ = "scan_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tllm_profile_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    attack_classes = Column(String, nullable=False) # stored as json or comma separated
    mutation_strategies = Column(String, nullable=False) # stored as json or comma separated
    mutation_depth = Column(Integer, default=1)
    total_prompts_sent = Column(Integer, default=0)
    vulnerabilities_found = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
