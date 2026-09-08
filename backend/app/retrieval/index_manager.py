from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.retrieval.bm25 import BM25Retriever
from backend.app.retrieval.vector_store import VectorStore


class IndexManager:
    def __init__(self):
        self.bm25_retriever = BM25Retriever()
        self.vector_store = VectorStore()
        self.active_chunks: List[Dict[str, Any]] = []
        self._is_ready = False

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def build_indexes(self, db: Session) -> int:
        doc_repo = DocumentRepository(db)
        chunks = doc_repo.get_active_chunks_with_metadata()
        self.active_chunks = chunks
        
        self.bm25_retriever.index(chunks)
        self.vector_store.index(chunks)
        self._is_ready = len(chunks) > 0
        return len(chunks)


index_manager = IndexManager()
