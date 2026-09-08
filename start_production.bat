@echo off
echo =======================================================
echo Starting HealthEvidence LLM + RAG Assistant (Production)
echo =======================================================

echo [1/3] Building Production Frontend Assets...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed.
    exit /b %errorlevel%
)
cd ..

echo [2/3] Seeding and verifying verified medical corpus...
python scripts/seed_corpus.py

echo [3/3] Launching FastAPI Production Server on port 8000...
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
