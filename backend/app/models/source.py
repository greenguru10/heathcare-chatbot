import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    authority_tier: Mapped[str] = mapped_column(String(1), nullable=False)  # A, B, C, D
    authority_score: Mapped[float] = mapped_column(Float, default=1.0)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)  # government, academic, guideline
    license_notes: Mapped[str] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")
