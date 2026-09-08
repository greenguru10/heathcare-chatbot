from sqlalchemy.orm import Session
from backend.app.models.audit import AuditEvent
from backend.app.core.privacy import sanitize_audit_metadata


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, event_type: str, request_id: str = None, user_id: str = None, metadata: dict = None) -> AuditEvent:
        clean_meta = sanitize_audit_metadata(metadata or {})
        event = AuditEvent(
            event_type=event_type,
            request_id=request_id,
            user_id=user_id,
            metadata_json=clean_meta
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
