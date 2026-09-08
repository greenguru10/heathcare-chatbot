from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.sources import SourceResponse, CategoryResponse
from backend.app.services.source_service import SourceService
from backend.app.database.session import get_db

router = APIRouter()


@router.get("/sources", response_model=List[SourceResponse])
def get_sources(db: Session = Depends(get_db)):
    service = SourceService(db)
    return service.get_sources()


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    service = SourceService(db)
    return service.get_categories()
