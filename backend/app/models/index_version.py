import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.base import Base


class IndexVersion(Base):
    __tablename__ = "index_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    index_type: Mapped[str] = mapped_column(String(30), nullable=False)  # bm25, vector, reranker_cache
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=True)
    artifact_path: Mapped[str] = mapped_column(Text, nullable=True)
    corpus_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parameters_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
