from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field
from backend.app.core.constants import DocumentStatus


class DocumentBase(BaseModel):
    title: str = Field(..., max_length=500)
    source_id: str
    category_id: int
    document_type: str = "fact_sheet"
    source_url: Optional[str] = None
    language: str = "en"
    publication_date: Optional[date] = None
    effective_date: Optional[date] = None
    last_updated: Optional[date] = None
    version_label: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdateStatus(BaseModel):
    status: DocumentStatus
    superseded_by: Optional[str] = None


class ChunkResponse(BaseModel):
    id: str
    chunk_sequence: int
    title: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None
    raw_text: str
    token_count: int
    topic_tags: List[str] = Field(default_factory=list)
    active: bool

    class Config:
        from_attributes = True


class DocumentResponse(DocumentBase):
    id: str
    local_path: str
    content_hash: str
    status: str
    superseded_by: Optional[str] = None
    extraction_quality: Optional[float] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    source_name: Optional[str] = None
    category_slug: Optional[str] = None
    chunk_count: Optional[int] = 0

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    extracted_text: Optional[str] = None
    chunks: List[ChunkResponse] = Field(default_factory=list)
