from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from backend.app.database.session import get_db
from backend.app.models.source import SourceRegistry
from backend.app.models.document import Document
from backend.app.retrieval.index_manager import index_manager
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health")
def get_health_status(db: Session = Depends(get_db)):
    active_sources = db.scalar(select(func.count(SourceRegistry.id)).where(SourceRegistry.active == True)) or 0
    active_docs = db.scalar(select(func.count(Document.id)).where(Document.status == "active")) or 0

    return {
        "status": "ok",
        "database": "ok",
        "bm25_index": "ready" if index_manager.is_ready else "empty",
        "vector_index": "ready" if index_manager.is_ready else "empty",
        "llm_gateway": "ready",
        "active_source_count": active_sources,
        "active_document_count": active_docs,
        "version": settings.PROJECT_VERSION
    }
