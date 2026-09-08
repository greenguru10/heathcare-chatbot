import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import configure_logging, logger
from backend.app.database.session import init_db, SessionLocal
from backend.app.retrieval.index_manager import index_manager
from backend.app.api.router import api_router
from backend.app.core.exceptions import HealthcareAppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Initializing database schema...")
    try:
        init_db()
    except Exception as e:
        logger.error("Database schema init warning (will retry on query)", error=str(e))
    
    # Initialize in-memory hybrid search indexes from DB
    logger.info("Building hybrid retrieval indexes...")
    try:
        db = SessionLocal()
        try:
            count = index_manager.build_indexes(db)
            logger.info("Hybrid indexes built successfully", active_chunks=count)
        finally:
            db.close()
    except Exception as e:
        logger.error("Hybrid index build warning (will build on-demand)", error=str(e))

    yield

    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.PROJECT_VERSION,
        description="Educational Healthcare LLM + RAG Assistant API with strict safety bounds.",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        lifespan=lifespan
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Performance Tracking Middleware
    @app.middleware("http")
    async def request_timing_and_id_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:8]}"
        start_time = time.perf_counter()
        
        response: Response = await call_next(request)
        
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response

    # Exception Handlers
    @app.exception_handler(HealthcareAppException)
    async def healthcare_exception_handler(request: Request, exc: HealthcareAppException):
        logger.warn("Healthcare application error", message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": exc.message, "details": exc.details}
        )

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Mount Frontend Static Assets for Single-Container Production Serving
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist_dir.exists():
        assets_dir = dist_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa_frontend(full_path: str):
            # If requesting a specific file that exists in dist, serve it
            file_path = dist_dir / full_path
            if full_path and file_path.is_file():
                return FileResponse(file_path)
            # Otherwise return index.html for client-side SPA routing
            return FileResponse(dist_dir / "index.html")

    return app


app = create_app()
