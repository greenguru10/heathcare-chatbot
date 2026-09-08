from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.core.constants import RiskLevel, ResponseMode


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=1500, description="User health query")
    session_id: Optional[str] = Field(None, description="Unique session UUID")
    locale: Optional[str] = Field("en-IN", description="BCP-47 locale tag")


class SourceCitationResponse(BaseModel):
    citation_key: str  # e.g. S1, S2
    title: str
    source_name: str
    authority_tier: str  # A, B, C, D
    section: Optional[str] = None
    publication_date: Optional[str] = None
    last_updated: Optional[str] = None
    url: Optional[str] = None
    excerpt: str


class ConfidenceResponse(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    label: str  # high, medium, low, insufficient
    explanation: str


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    response_mode: ResponseMode
    risk_level: RiskLevel
    answer: str
    key_points: List[str] = Field(default_factory=list)
    when_to_seek_care: Optional[str] = None
    limitations: Optional[str] = None
    confidence: ConfidenceResponse
    sources: List[SourceCitationResponse] = Field(default_factory=list)
    follow_up_suggestions: List[str] = Field(default_factory=list)
