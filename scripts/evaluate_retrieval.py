import sys
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.database.session import SessionLocal, init_db
from backend.app.services.evaluation_service import EvaluationService
from backend.app.retrieval.index_manager import index_manager


def run_retrieval_eval():
    init_db()
    db = SessionLocal()
    # Ensure indexes are built
    index_manager.build_indexes(db)
    
    eval_svc = EvaluationService(db)
    results = eval_svc.evaluate_retrieval_benchmark()
    db.close()

    print("========================================")
    print("     RETRIEVAL PERFORMANCE BENCHMARK     ")
    print("========================================")
    print(f"Total Eval Queries:    {results.get('total_eval_queries')}")
    print(f"Recall@5:              {results.get('recall_at_5') * 100:.1f}% (Target: >= 85.0%)")
    print(f"Recall@10:             {results.get('recall_at_10') * 100:.1f}% (Target: >= 93.0%)")
    print(f"MRR:                   {results.get('mrr'):.3f}")
    print(f"Target Met:            {results.get('recall_target_met')}")
    print("========================================")


if __name__ == "__main__":
    run_retrieval_eval()
