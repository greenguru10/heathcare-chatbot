from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.database.repositories.source_repo import SourceRepository
from backend.app.ingestion.pipeline import ingestion_pipeline
from backend.app.retrieval.index_manager import index_manager
from backend.app.models.document import Document
from backend.app.core.exceptions import EntityNotFoundException, DocumentIngestionException


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.source_repo = SourceRepository(db)

    def ingest_file(
        self,
        file_path: Path,
        source_id: str,
        category_id: int,
        title_override: Optional[str] = None,
        source_url_override: Optional[str] = None
    ) -> Document:
        source = self.source_repo.get_source_by_id(source_id)
        if not source:
            raise EntityNotFoundException(f"Source with id '{source_id}' not found.")

        category = self.source_repo.get_category_by_id(category_id)
        if not category:
            raise EntityNotFoundException(f"Category with id '{category_id}' not found.")

        result = ingestion_pipeline.process_file(
            file_path=file_path,
            source_id=source_id,
            category_id=category_id,
            title_override=title_override,
            source_url_override=source_url_override
        )

        doc_data = result["document"]
        existing = self.doc_repo.get_document_by_hash(doc_data["content_hash"])
        if existing:
            return existing

        created_doc = self.doc_repo.create_document(doc_data)

        # Attach document_id to chunks
        chunks_data = result["chunks"]
        for c in chunks_data:
            c["document_id"] = created_doc.id

        self.doc_repo.add_chunks(chunks_data)

        # Update in-memory indexes
        index_manager.build_indexes(self.db)

        return created_doc

    def get_documents(self, status: Optional[str] = None, category_slug: Optional[str] = None, skip: int = 0, limit: int = 50):
        return self.doc_repo.get_documents(status=status, category_slug=category_slug, skip=skip, limit=limit)

    def get_document(self, document_id: str) -> Optional[Document]:
        return self.doc_repo.get_document_by_id(document_id)

    def update_document_status(self, document_id: str, status: str, superseded_by: Optional[str] = None) -> Optional[Document]:
        doc = self.doc_repo.update_document_status(document_id, status, superseded_by)
        if doc:
            index_manager.build_indexes(self.db)
        return doc

    def reindex_all(self) -> int:
        return index_manager.build_indexes(self.db)
