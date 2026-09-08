from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.schemas.sessions import (
    SessionDetailResponse,
    SessionSummaryResponse,
    CreateSessionRequest,
    RenameSessionRequest,
    MessageResponse
)
from backend.app.services.session_service import SessionService
from backend.app.database.session import get_db

router = APIRouter()


@router.get("/sessions", response_model=List[SessionSummaryResponse])
def list_sessions(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    service = SessionService(db)
    return service.list_sessions(user_id=user_id, limit=limit)


@router.post("/sessions", response_model=SessionSummaryResponse)
def create_session(request: CreateSessionRequest = CreateSessionRequest(), db: Session = Depends(get_db)):
    service = SessionService(db)
    session = service.create_session(title=request.title, user_id=request.user_id)
    return SessionSummaryResponse(
        id=session.id,
        title=service._derive_session_title(session),
        message_count=0,
        user_id=session.user_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        last_message_preview=None,
        risk_level="green"
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    service = SessionService(db)
    session = service.get_session_history(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            metadata_json=m.metadata_json or {},
            created_at=m.created_at
        )
        for m in sorted(session.messages, key=lambda x: x.created_at)
    ]

    title = service._derive_session_title(session)

    return SessionDetailResponse(
        id=session.id,
        title=title,
        user_id=session.user_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        state_json=session.state_json or {},
        messages=messages
    )


@router.patch("/sessions/{session_id}", response_model=SessionDetailResponse)
def rename_session(session_id: str, request: RenameSessionRequest, db: Session = Depends(get_db)):
    service = SessionService(db)
    session = service.rename_session(session_id, request.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            metadata_json=m.metadata_json or {},
            created_at=m.created_at
        )
        for m in sorted(session.messages, key=lambda x: x.created_at)
    ]

    return SessionDetailResponse(
        id=session.id,
        title=request.title,
        user_id=session.user_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        state_json=session.state_json or {},
        messages=messages
    )


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    service = SessionService(db)
    deleted = service.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session and associated conversational history deleted successfully."}


@router.delete("/sessions")
def delete_all_sessions(user_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = SessionService(db)
    count = service.delete_all_sessions(user_id=user_id)
    return {"message": f"Deleted {count} session(s) successfully.", "deleted_count": count}
