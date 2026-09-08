import sys
import argparse
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.database.session import SessionLocal, init_db
from backend.app.services.ingestion_service import IngestionService


def main():
    parser = argparse.ArgumentParser(description="Document review and status CLI")
    parser.add_argument("--list", action="store_true", help="List all documents")
    parser.add_argument("--doc-id", type=str, help="Document UUID")
    parser.add_argument("--status", type=str, choices=["active", "inactive", "superseded", "draft"], help="New status")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    svc = IngestionService(db)

    if args.list:
        docs, total = svc.get_documents()
        print(f"Total documents: {total}\n")
        for d in docs:
            print(f"[{d.id}] {d.title} | Status: {d.status} | Chunks: {len(d.chunks)}")
    elif args.doc_id and args.status:
        updated = svc.update_document_status(args.doc_id, args.status)
        if updated:
            print(f"Document {updated.id} status updated to {updated.status}")
        else:
            print("Document not found.")
    else:
        parser.print_help()

    db.close()


if __name__ == "__main__":
    main()
