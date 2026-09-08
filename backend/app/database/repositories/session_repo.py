from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from backend.app.models.session import SessionModel
from backend.app.models.message import Message


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> SessionModel:
        if session_id:
            stmt = select(SessionModel).where(SessionModel.id == session_id).options(joinedload(SessionModel.messages))
            session = self.db.scalars(stmt).unique().first()
            if session:
                return session

        new_session = SessionModel(user_id=user_id)
        if session_id:
            new_session.id = session_id
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def get_session(self, session_id: str) -> Optional[SessionModel]:
        stmt = select(SessionModel).where(SessionModel.id == session_id).options(
            joinedload(SessionModel.messages)
        )
        return self.db.scalars(stmt).unique().first()

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[dict] = None) -> Message:
        msg = Message(
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=metadata or {}
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def list_sessions(self, user_id: Optional[str] = None, limit: int = 50) -> List[SessionModel]:
        stmt = select(SessionModel).options(joinedload(SessionModel.messages)).order_by(SessionModel.updated_at.desc()).limit(limit)
        if user_id:
            stmt = stmt.where(SessionModel.user_id == user_id)
        return list(self.db.scalars(stmt).unique().all())

    def rename_session(self, session_id: str, title: str) -> Optional[SessionModel]:
        session = self.db.get(SessionModel, session_id)
        if session:
            state = dict(session.state_json or {})
            state["title"] = title
            session.state_json = state
            self.db.commit()
            self.db.refresh(session)
            return session
        return None

    def update_session_state(self, session_id: str, state_json: dict):
        session = self.db.get(SessionModel, session_id)
        if session:
            current_state = dict(session.state_json or {})
            current_state.update(state_json)
            session.state_json = current_state
            self.db.commit()

    def delete_session(self, session_id: str) -> bool:
        session = self.db.get(SessionModel, session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

    def delete_all_sessions(self, user_id: Optional[str] = None) -> int:
        stmt = select(SessionModel)
        if user_id:
            stmt = stmt.where(SessionModel.user_id == user_id)
        sessions = self.db.scalars(stmt).all()
        count = len(sessions)
        for s in sessions:
            self.db.delete(s)
        self.db.commit()
        return count
