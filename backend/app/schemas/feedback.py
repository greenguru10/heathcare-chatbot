from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    answer_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str = Field("helpful", max_length=50)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    answer_id: str
    rating: int
    feedback_type: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
