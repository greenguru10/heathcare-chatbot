from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.source import SourceRegistry
from backend.app.models.category import Category


class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_sources(self, active_only: bool = True) -> List[SourceRegistry]:
        stmt = select(SourceRegistry)
        if active_only:
            stmt = stmt.where(SourceRegistry.active == True)
        return list(self.db.scalars(stmt).all())

    def get_source_by_id(self, source_id: str) -> Optional[SourceRegistry]:
        return self.db.get(SourceRegistry, source_id)

    def get_source_by_name(self, name: str) -> Optional[SourceRegistry]:
        stmt = select(SourceRegistry).where(SourceRegistry.name == name)
        return self.db.scalars(stmt).first()

    def create_source(self, source_data: dict) -> SourceRegistry:
        source = SourceRegistry(**source_data)
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_all_categories(self, active_only: bool = True) -> List[Category]:
        stmt = select(Category)
        if active_only:
            stmt = stmt.where(Category.active == True)
        return list(self.db.scalars(stmt).all())

    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        stmt = select(Category).where(Category.slug == slug)
        return self.db.scalars(stmt).first()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.get(Category, category_id)

    def create_category(self, category_data: dict) -> Category:
        category = Category(**category_data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
