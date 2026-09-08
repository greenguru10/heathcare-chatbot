from typing import Optional
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str


class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str
    role: str = "user"


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    role: str
    status: str

    class Config:
        from_attributes = True
