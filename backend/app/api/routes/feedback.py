from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse
from backend.app.database.repositories.chat_repo import ChatRepository
from backend.app.database.session import get_db

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(feedback_in: FeedbackCreate, db: Session = Depends(get_db)):
    repo = ChatRepository(db)
    feedback_data = feedback_in.model_dump()
    created = repo.add_feedback(feedback_data)
    return FeedbackResponse(
        id=created.id,
        answer_id=created.answer_id,
        rating=created.rating,
        feedback_type=created.feedback_type,
        comment=created.comment,
        created_at=created.created_at
    )
