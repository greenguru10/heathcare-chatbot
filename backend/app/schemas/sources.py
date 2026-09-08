from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    name: str = Field(..., max_length=255)
    base_url: str
    authority_tier: str = Field(..., max_length=1)  # A, B, C, D
    authority_score: float = Field(1.0, ge=0.0, le=1.0)
    source_type: str = Field(..., max_length=80)
    license_notes: Optional[str] = None
    active: bool = True


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    slug: str
    display_name: str
    description: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True
