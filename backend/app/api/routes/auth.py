from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from backend.app.models.user import User
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.database.session import get_db

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email)
    user = db.scalars(stmt).first()
    if not user or not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token({"sub": user.id, "role": user.role, "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        email=user.email
    )


@router.post("/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    existing = db.scalars(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed,
        role=user_in.role,
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        status=new_user.status
    )
