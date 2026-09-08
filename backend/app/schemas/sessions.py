from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True


class SessionSummaryResponse(BaseModel):
    id: str
    title: str
    message_count: int
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_message_preview: Optional[str] = None
    risk_level: Optional[str] = None

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    id: str
    title: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    state_json: Dict[str, Any] = Field(default_factory=dict)
    messages: List[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None
    user_id: Optional[str] = None


class RenameSessionRequest(BaseModel):
    title: str
