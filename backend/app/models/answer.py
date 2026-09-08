import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("queries.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    model_provider: Mapped[str] = mapped_column(String(100), default="system")
    model_name: Mapped[str] = mapped_column(String(255), default="grounded_rag_v1")
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    response_mode: Mapped[str] = mapped_column(String(50), default="grounded_answer")
    
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    key_points_json: Mapped[dict] = mapped_column(JSON, default=list)
    when_to_seek_care: Mapped[str] = mapped_column(Text, nullable=True)
    limitations: Mapped[str] = mapped_column(Text, nullable=True)
    
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    confidence_label: Mapped[str] = mapped_column(String(20), default="high")
    confidence_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    grounding_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    safety_flags: Mapped[dict] = mapped_column(JSON, default=list)
    token_usage_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    query = relationship("QueryRecord", back_populates="answer")
    citations = relationship("Citation", back_populates="answer", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="answer", cascade="all, delete-orphan")
