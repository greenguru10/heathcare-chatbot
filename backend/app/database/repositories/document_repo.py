from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.models.source import SourceRegistry
from backend.app.models.category import Category


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_documents(
        self,
        status: Optional[str] = None,
        category_slug: Optional[str] = None,
        source_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Document], int]:
        stmt = select(Document).options(
            joinedload(Document.source),
            joinedload(Document.category),
            joinedload(Document.chunks)
        )
        conditions = []
        if status:
            conditions.append(Document.status == status)
        if source_id:
            conditions.append(Document.source_id == source_id)
        if category_slug:
            stmt = stmt.join(Document.category)
            conditions.append(Category.slug == category_slug)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Total count
        count_stmt = select(func.count(Document.id))
        if conditions:
            if category_slug:
                count_stmt = count_stmt.join(Document.category)
            count_stmt = count_stmt.where(and_(*conditions))
        total = self.db.scalar(count_stmt) or 0

        stmt = stmt.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).unique().all())
        return items, total

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id).options(
            joinedload(Document.source),
            joinedload(Document.category),
            joinedload(Document.chunks)
        )
        return self.db.scalars(stmt).unique().first()

    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        stmt = select(Document).where(Document.content_hash == content_hash)
        return self.db.scalars(stmt).first()

    def create_document(self, document_data: dict) -> Document:
        doc = Document(**document_data)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def update_document_status(self, document_id: str, status: str, superseded_by: Optional[str] = None) -> Optional[Document]:
        doc = self.get_document_by_id(document_id)
        if not doc:
            return None
        doc.status = status
        if superseded_by:
            doc.superseded_by = superseded_by
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def add_chunks(self, chunks_data: List[dict]) -> List[DocumentChunk]:
        chunks = [DocumentChunk(**data) for data in chunks_data]
        self.db.add_all(chunks)
        self.db.commit()
        return chunks

    def get_active_chunks_with_metadata(self) -> List[dict]:
        """Returns all chunks belonging to active documents, joined with source authority."""
        stmt = (
            select(DocumentChunk, Document, SourceRegistry, Category)
            .join(Document, DocumentChunk.document_id == Document.id)
            .join(SourceRegistry, Document.source_id == SourceRegistry.id)
            .join(Category, Document.category_id == Category.id)
            .where(
                Document.status == "active",
                DocumentChunk.active == True,
                SourceRegistry.active == True
            )
        )
        results = self.db.execute(stmt).all()
        chunks_meta = []
        for chunk, doc, src, cat in results:
            chunks_meta.append({
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "title": chunk.title or doc.title,
                "section": chunk.section,
                "subsection": chunk.subsection,
                "raw_text": chunk.raw_text,
                "normalized_text": chunk.normalized_text,
                "token_count": chunk.token_count,
                "topic_tags": chunk.topic_tags or [],
                "source_name": src.name,
                "source_url": doc.source_url or src.base_url,
                "authority_tier": src.authority_tier,
                "authority_score": src.authority_score,
                "category_slug": cat.slug,
                "publication_date": str(doc.publication_date) if doc.publication_date else None,
                "last_updated": str(doc.last_updated) if doc.last_updated else None,
            })
        return chunks_meta
