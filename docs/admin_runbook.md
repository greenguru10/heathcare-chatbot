# Admin Runbook & Operations

## 1. Document Management Lifecycle
- **Ingestion**: Admin uploads documents via UI (`/api/v1/documents`) or runs `python scripts/ingest_directory.py`.
- **Review**: Admin inspects parsed chunks and quality score in the Admin Portal.
- **Activation/Supersession**: Status can be set to `active`, `inactive`, or `superseded` via UI or `python scripts/review_document.py --doc-id <UUID> --status active`.
- **Reindexing**: Rebuilds BM25 and vector stores after document status changes (`POST /api/v1/reindex`).

## 2. API Key Management
- Admin operations require the header `X-API-Key: <ADMIN_API_KEY>` (configured in `.env`).
