from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.core.config import settings
from backend.app.core.security import verify_token


def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    return verify_token(token)


def require_admin(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    user_payload: Optional[dict] = Depends(get_current_user_optional)
):
    # Allow either valid admin API key or admin JWT
    if x_api_key and x_api_key == settings.ADMIN_API_KEY:
        return {"role": "admin", "type": "api_key"}

    if user_payload and user_payload.get("role") in ["admin", "reviewer"]:
        return user_payload

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authorization required (Provide valid X-API-Key or Bearer token)."
    )
