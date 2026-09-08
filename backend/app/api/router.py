from fastapi import APIRouter
from backend.app.api.routes import health, chat, sources, documents, sessions, feedback, auth

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(sources.router, tags=["Sources & Categories"])
api_router.include_router(documents.router, tags=["Documents"])
api_router.include_router(sessions.router, tags=["Sessions"])
api_router.include_router(feedback.router, tags=["Feedback"])
api_router.include_router(auth.router, tags=["Auth"])
