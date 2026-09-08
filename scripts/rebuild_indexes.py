import sys
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.database.session import SessionLocal, init_db
from backend.app.retrieval.index_manager import index_manager


def rebuild():
    init_db()
    db = SessionLocal()
    count = index_manager.build_indexes(db)
    print(f"Hybrid search indexes rebuilt successfully. Total active chunks indexed: {count}")
    db.close()


if __name__ == "__main__":
    rebuild()
