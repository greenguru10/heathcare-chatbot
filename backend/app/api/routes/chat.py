from fastapi import APIRouter, Depends, Header, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.chat_service import ChatService
from backend.app.database.session import get_db

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    request: ChatRequest,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    db: Session = Depends(get_db)
):
    service = ChatService(db)
    return await service.answer(request, request_id=x_request_id)
