from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.repositories.session_repo import SessionRepository
from backend.app.models.session import SessionModel


class SessionService:
    def __init__(self, db: Session):
        self.repo = SessionRepository(db)

    def list_sessions(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        sessions = self.repo.list_sessions(user_id=user_id, limit=limit)
        results = []
        for s in sessions:
            title = self._derive_session_title(s)
            msgs = s.messages or []
            last_msg = msgs[-1].content if msgs else None
            if last_msg and len(last_msg) > 60:
                last_msg = last_msg[:60] + "..."
            
            risk = (s.state_json or {}).get("previous_risk_level", "green")
            results.append({
                "id": s.id,
                "title": title,
                "message_count": len(msgs),
                "user_id": s.user_id,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "last_message_preview": last_msg,
                "risk_level": risk
            })
        return results

    def create_session(self, title: Optional[str] = None, user_id: Optional[str] = None) -> SessionModel:
        session = self.repo.get_or_create_session(user_id=user_id)
        if title:
            self.repo.rename_session(session.id, title)
        return session

    def get_session_history(self, session_id: str) -> Optional[SessionModel]:
        return self.repo.get_session(session_id)

    def rename_session(self, session_id: str, title: str) -> Optional[SessionModel]:
        return self.repo.rename_session(session_id, title)

    def delete_session(self, session_id: str) -> bool:
        return self.repo.delete_session(session_id)

    def delete_all_sessions(self, user_id: Optional[str] = None) -> int:
        return self.repo.delete_all_sessions(user_id=user_id)

    def _derive_session_title(self, session: SessionModel) -> str:
        state = session.state_json or {}
        if state.get("title"):
            return state["title"]
        
        # Check first user message
        if session.messages:
            for m in session.messages:
                if m.role == "user" and m.content:
                    clean = m.content.strip()
                    if len(clean) > 35:
                        return clean[:35] + "..."
                    return clean
        
        # Fallback to topic
        topics = state.get("previous_topics", [])
        if topics:
            return topics[0]
            
        return f"Health Consultation {session.id[:8]}"
