# System Architecture & Technical Specifications

## 1. Executive Overview
HealthEvidence is an educational Healthcare LLM + Retrieval-Augmented Generation (RAG) assistant that answers health-literacy inquiries strictly from curated, authoritative, versioned public-health corpora (WHO, CDC, MedlinePlus, ICMR).

## 2. Core Architecture Pipeline
```
User Query
  ├── 1. Data Minimization & PII Redaction
  ├── 2. Deterministic Safety Triage Gate
  │      ├── Emergency Red Flags -> Immediate Emergency Guidance (No LLM / No Retrieval)
  │      ├── Crisis / Self-Harm -> Immediate Crisis Hotlines (112 / 988)
  │      ├── Medication / Prescribing Advice -> Deferral & Refusal
  │      └── Personal Diagnosis Demands -> Clinical Deferral
  ├── 3. Conversation Context & Follow-Up Entity Resolution
  ├── 4. Hybrid Retrieval Pipeline
  │      ├── BM25 Lexical Retrieval (k1=1.2, b=0.75)
  │      ├── Dense Vector Semantic Search
  │      ├── Reciprocal Rank Fusion (RRF k=60)
  │      ├── Cross-Encoder / Overlap Reranking
  │      └── Document-Diversity Evidence Selection (3-5 chunks max)
  ├── 5. Guarded Prompt Construction with Strict [S#] Citation Envelopes
  ├── 6. LLM Gateway Generation (Low Temperature: 0.0, Structured JSON)
  ├── 7. Verification & Grounding Guardrails
  │      ├── Citation Validator (No phantom/invalid citation tags)
  │      ├── Claim-to-Evidence Grounding Validator (Lexical/Semantic support)
  │      └── Output Safety Validator (Filter prohibited diagnosis/prescribing claims)
  ├── 8. Multi-Factor Confidence Scorer
  └── 9. Response Delivery & Audit Event Persistence
```

## 3. Technology Stack
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite/PostgreSQL with pgvector support
- **Retrieval:** BM25 (`rank-bm25`), Dense Vectorizer (`sentence-transformers` / fast TF-IDF), Reciprocal Rank Fusion
- **LLM Gateway:** Multi-provider interface supporting OpenAI-compatible APIs, Google Gemini, Anthropic, Ollama, and deterministic Mock Provider for offline execution
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
