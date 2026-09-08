from typing import List, Dict, Any
from backend.app.retrieval.index_manager import index_manager
from backend.app.retrieval.hybrid import HybridRanker
from backend.app.retrieval.reranker import reranker
from backend.app.retrieval.evidence import evidence_selector
from backend.app.core.config import settings


class HybridRetriever:
    def __init__(self):
        self.hybrid_ranker = HybridRanker()

    def retrieve(
        self,
        query: str,
        candidate_k: int = settings.RETRIEVAL_CANDIDATE_K,
        top_n: int = settings.RERANK_TOP_N,
        final_k: int = settings.FINAL_EVIDENCE_K,
    ) -> Dict[str, Any]:
        """
        Full hybrid retrieval pipeline:
        1. BM25 Search
        2. Vector Similarity Search
        3. Reciprocal Rank Fusion
        4. Cross-Encoder Reranking
        5. Diversity Evidence Selection
        """
        # 1. BM25
        bm25_results = index_manager.bm25_retriever.search(query, top_k=candidate_k)

        # 2. Vector
        vector_results = index_manager.vector_store.search(query, top_k=candidate_k)

        # 3. Hybrid RRF
        candidates = self.hybrid_ranker.fuse(bm25_results, vector_results)

        # 4. Rerank
        reranked = reranker.rerank(query, candidates, top_n=top_n)

        # 5. Evidence Selection
        evidence = evidence_selector.select(reranked)

        return {
            "all_candidates": reranked,
            "evidence_chunks": evidence,
            "total_candidates": len(reranked)
        }


retriever = HybridRetriever()
