import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.schemas.documents import DocumentResponse, DocumentDetailResponse, DocumentUpdateStatus
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.ingestion_service import IngestionService
from backend.app.api.dependencies import require_admin
from backend.app.database.session import get_db
from backend.app.core.config import settings

router = APIRouter()


@router.get("/documents", response_model=PaginatedResponse[DocumentResponse])
def list_documents(
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    service = IngestionService(db)
    skip = (page - 1) * page_size
    items, total = service.get_documents(status=status, category_slug=category, skip=skip, limit=page_size)
    
    docs_resp = []
    for d in items:
        docs_resp.append(DocumentResponse(
            id=d.id,
            title=d.title,
            source_id=d.source_id,
            category_id=d.category_id,
            document_type=d.document_type,
            source_url=d.source_url,
            language=d.language,
            publication_date=d.publication_date,
            effective_date=d.effective_date,
            last_updated=d.last_updated,
            version_label=d.version_label,
            local_path=d.local_path,
            content_hash=d.content_hash,
            status=d.status,
            superseded_by=d.superseded_by,
            extraction_quality=d.extraction_quality,
            reviewed_at=d.reviewed_at,
            created_at=d.created_at,
            updated_at=d.updated_at,
            source_name=d.source.name if d.source else None,
            category_slug=d.category.slug if d.category else None,
            chunk_count=len(d.chunks)
        ))

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
    return PaginatedResponse(
        items=docs_resp,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
def get_document_detail(document_id: str, db: Session = Depends(get_db)):
    service = IngestionService(db)
    doc = service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks_resp = [
        {
            "id": c.id,
            "chunk_sequence": c.chunk_sequence,
            "title": c.title,
            "section": c.section,
            "subsection": c.subsection,
            "raw_text": c.raw_text,
            "token_count": c.token_count,
            "topic_tags": c.topic_tags or [],
            "active": c.active
        }
        for c in doc.chunks
    ]

    return DocumentDetailResponse(
        id=doc.id,
        title=doc.title,
        source_id=doc.source_id,
        category_id=doc.category_id,
        document_type=doc.document_type,
        source_url=doc.source_url,
        language=doc.language,
        publication_date=doc.publication_date,
        effective_date=doc.effective_date,
        last_updated=doc.last_updated,
        version_label=doc.version_label,
        local_path=doc.local_path,
        content_hash=doc.content_hash,
        status=doc.status,
        superseded_by=doc.superseded_by,
        extraction_quality=doc.extraction_quality,
        reviewed_at=doc.reviewed_at,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        source_name=doc.source.name if doc.source else None,
        category_slug=doc.category.slug if doc.category else None,
        chunk_count=len(doc.chunks),
        extracted_text=doc.extracted_text,
        chunks=chunks_resp
    )


@router.post("/documents", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    source_id: str = Form(...),
    category_id: int = Form(...),
    title: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    service = IngestionService(db)
    upload_dir = settings.DATA_DIR / "raw" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = upload_dir / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc = service.ingest_file(
            file_path=dest_path,
            source_id=source_id,
            category_id=category_id,
            title_override=title,
            source_url_override=source_url
        )
        return DocumentResponse(
            id=doc.id,
            title=doc.title,
            source_id=doc.source_id,
            category_id=doc.category_id,
            document_type=doc.document_type,
            source_url=doc.source_url,
            language=doc.language,
            publication_date=doc.publication_date,
            effective_date=doc.effective_date,
            last_updated=doc.last_updated,
            version_label=doc.version_label,
            local_path=doc.local_path,
            content_hash=doc.content_hash,
            status=doc.status,
            superseded_by=doc.superseded_by,
            extraction_quality=doc.extraction_quality,
            reviewed_at=doc.reviewed_at,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            source_name=doc.source.name if doc.source else None,
            category_slug=doc.category.slug if doc.category else None,
            chunk_count=len(doc.chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/documents/{document_id}", response_model=DocumentResponse)
def update_document_lifecycle(
    document_id: str,
    update: DocumentUpdateStatus,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    service = IngestionService(db)
    doc = service.update_document_status(document_id, update.status.value, update.superseded_by)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        source_id=doc.source_id,
        category_id=doc.category_id,
        document_type=doc.document_type,
        source_url=doc.source_url,
        language=doc.language,
        publication_date=doc.publication_date,
        effective_date=doc.effective_date,
        last_updated=doc.last_updated,
        version_label=doc.version_label,
        local_path=doc.local_path,
        content_hash=doc.content_hash,
        status=doc.status,
        superseded_by=doc.superseded_by,
        extraction_quality=doc.extraction_quality,
        reviewed_at=doc.reviewed_at,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        source_name=doc.source.name if doc.source else None,
        category_slug=doc.category.slug if doc.category else None,
        chunk_count=len(doc.chunks)
    )


@router.post("/reindex")
def trigger_reindex(admin=Depends(require_admin), db: Session = Depends(get_db)):
    service = IngestionService(db)
    count = service.reindex_all()
    return {"message": "Reindexing complete", "active_chunks_indexed": count}
