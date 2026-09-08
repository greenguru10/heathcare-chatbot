#!/usr/bin/env bash
set -e

echo "======================================================="
echo "Starting HealthEvidence LLM + RAG Assistant (Production)"
echo "======================================================="

# Build Frontend
if [ -d "frontend" ]; then
    echo "[1/3] Building Production Frontend Assets..."
    cd frontend && npm ci && npm run build && cd ..
fi

# Seed Corpus if DB empty
echo "[2/3] Checking & Seeding Knowledge Base..."
python scripts/seed_corpus.py || true

# Start Multi-Worker Production Server
echo "[3/3] Launching Production Gunicorn/Uvicorn Workers..."
exec gunicorn backend.app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
