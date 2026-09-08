from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.database.repositories.source_repo import SourceRepository
from backend.app.models.source import SourceRegistry
from backend.app.models.category import Category


class SourceService:
    def __init__(self, db: Session):
        self.repo = SourceRepository(db)

    def get_sources(self) -> List[SourceRegistry]:
        return self.repo.get_all_sources(active_only=True)

    def get_categories(self) -> List[Category]:
        return self.repo.get_all_categories(active_only=True)
