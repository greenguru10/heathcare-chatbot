# HealthEvidence - Healthcare LLM + RAG Assistant

> **Educational Health Information System with Retrieval-Augmented Generation (RAG).**
> 
> **Safety Boundary:** This system provides health literacy education grounded in verified public-health publications. It is **not** a diagnostic device, emergency service, prescribing tool, or substitute for licensed clinician advice.

---

## 🌟 Key Features
- **Deterministic Safety Triage Gate:** Emergency red-flags (chest pain, stroke, unresponsiveness, poison, self-harm) and prohibited requests (diagnosis demands, medication prescribing) are routed immediately to emergency guidance with zero LLM generation or retrieval latency.
- **Hybrid Retrieval Pipeline:** Combines BM25 lexical search with dense vector similarity, Reciprocal Rank Fusion (RRF k=60), and cross-scoring reranking.
- **Strict Grounding & Verifiable Citations:** Answers are constrained strictly to retrieved context. Every factual sentence carries verifiable `[S1]`, `[S2]` citation badges linking to authoritative source excerpts.
- **Multi-Factor Confidence Scoring:** Deterministic score calculated from retrieval relevance, grounding support, source authority tier, and corroboration.
- **Modern React + Vite + Tailwind Frontend:** Clean clinical UI with interactive source drawers, confidence badges, emergency cards, and an Admin Portal for document lifecycle management and retrieval diagnostics.
- **Pluggable Architecture:** Ready for local execution out-of-the-box (SQLite + fast TF-IDF / sentence-transformers + offline mock client) or production cloud deployment (PostgreSQL + pgvector + OpenAI/Gemini APIs).

---

## 🚀 Quick Start

### 1. Backend Setup
```powershell
# In root directory
pip install -r backend/requirements.txt

# Seed database with authoritative sources and ingest initial corpus
python scripts/seed_sources.py
python scripts/ingest_directory.py

# Run FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```
Swagger API docs: `http://localhost:8000/api/v1/docs`

### 2. Frontend Setup
```powershell
# In a new terminal
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Testing & Evaluation Benchmarks
```powershell
# Run backend test suite (19 unit & integration tests)
python -m pytest backend/tests -v

# Run Safety Benchmark (Emergency Recall >= 98%, Blocked Recall >= 95%)
python scripts/evaluate_safety.py

# Run Retrieval Performance Benchmark (Recall@5, Recall@10, MRR)
python scripts/evaluate_retrieval.py
```

---

## 🏛️ Documentation
- [Architecture & Tech Specs](docs/architecture.md)
- [Safety Policy & Clinical Governance](docs/safety_policy.md)
- [Dataset Registry & Authority Tiers](docs/dataset_registry.md)
- [Evaluation Protocol](docs/evaluation_protocol.md)
- [Deployment Guide](docs/deployment.md)
- [Admin Operations Runbook](docs/admin_runbook.md)

---

## 📜 License
MIT License.
