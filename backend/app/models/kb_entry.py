from sqlalchemy import Column, String
from app.database import Base
import uuid

class KBEntry(Base):
    __tablename__ = "kb_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attack_class = Column(String, nullable=False)
    title = Column(String, nullable=False)
    template = Column(String, nullable=False)
    tags = Column(String, nullable=True) # JSON list
    source = Column(String, nullable=True)
