# Deployment Guide

## 1. Local Development
```powershell
# 1. Seed database and ingest initial authoritative corpus
python scripts/seed_sources.py
python scripts/ingest_directory.py

# 2. Run backend FastAPI server
uvicorn backend.app.main:app --reload --port 8000

# 3. Run frontend Vite server (in a separate terminal)
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

## 2. Docker Deployment
```bash
docker-compose up --build
```
- Backend API: `http://localhost:8000/api/v1`
- Swagger OpenAPI docs: `http://localhost:8000/api/v1/docs`
- PostgreSQL pgvector container on port 5432.

## 3. Cloud Deployment (Render / Railway)
- Deploy backend service using `backend/Dockerfile`.
- Attach persistent PostgreSQL database.
- Supply environment variables from `.env.example`.
