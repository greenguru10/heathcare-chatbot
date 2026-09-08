from pathlib import Path
from typing import List, Optional, Union, Any
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Healthcare LLM + RAG Assistant"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Base Paths
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = ROOT_DIR / "data"
    CONFIGS_DIR: Path = ROOT_DIR / "configs"

    # Database
    # Default to local SQLite for lightweight standalone usage, can be set to PostgreSQL in .env
    DATABASE_URL: str = "sqlite:///./health_rag.db"
    ENABLE_PGVECTOR: bool = False

    # Security & Auth
    JWT_SECRET: str = "health_rag_insecure_development_secret_key_change_in_prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_API_KEY: str = "health_rag_admin_secret_key_2026"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if not v_clean:
                return ["*"]
            if (v_clean.startswith("[") and v_clean.endswith("]")) or (v_clean.startswith("(") and v_clean.endswith(")")):
                try:
                    parsed = json.loads(v_clean)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                except Exception:
                    pass
            # Comma-separated or single string
            return [item.strip().strip("'\"") for item in v_clean.split(",") if item.strip()]
        elif isinstance(v, (list, tuple, set)):
            return [str(item) for item in v]
        return ["*"]

    # LLM Gateway
    LLM_PROVIDER: str = "mock"  # options: mock, openai_compatible, gemini, anthropic, ollama
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_OUTPUT_TOKENS: int = 700
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_RETRIES: int = 2

    # Embeddings & Reranker
    EMBEDDING_PROVIDER: str = "local"  # options: local, tfidf_fast, openai
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    VECTOR_DIMENSION: int = 384

    # Retrieval & Limits
    RETRIEVAL_CANDIDATE_K: int = 40
    RERANK_TOP_N: int = 30
    FINAL_EVIDENCE_K: int = 4
    MIN_RETRIEVAL_SCORE: float = 0.45
    MIN_GROUNDING_SCORE: float = 0.70

    MAX_UPLOAD_MB: int = 25
    MAX_QUERY_LENGTH: int = 1500
    RATE_LIMIT_PER_MINUTE: int = 30

    # Regional config
    DEFAULT_REGION: str = "IN"  # IN, US, UK, DEFAULT
    LOG_LEVEL: str = "INFO"

    # Uptime Keep-Alive Bot
    UPTIME_BOT_ENABLED: bool = True
    UPTIME_PING_URL: str = "https://heathcare-chatbot-2.onrender.com/api/v1/health"
    UPTIME_PING_INTERVAL_MINUTES: int = 10


settings = Settings()
