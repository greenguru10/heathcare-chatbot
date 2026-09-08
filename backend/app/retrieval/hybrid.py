from typing import List, Dict, Any, Tuple
from collections import defaultdict


class HybridRanker:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def fuse(
        self,
        bm25_results: List[Tuple[Dict[str, Any], float]],
        vector_results: List[Tuple[Dict[str, Any], float]],
    ) -> List[Dict[str, Any]]:
        """
        Merges lexical BM25 and dense vector candidates using Reciprocal Rank Fusion (RRF).
        """
        chunk_dict: Dict[str, Dict[str, Any]] = {}
        bm25_scores: Dict[str, float] = {}
        vector_scores: Dict[str, float] = {}
        rrf_scores: Dict[str, float] = defaultdict(float)

        # Process BM25 ranks
        for rank, (chunk, score) in enumerate(bm25_results):
            cid = chunk["chunk_id"]
            chunk_dict[cid] = chunk
            bm25_scores[cid] = score
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank + 1)

        # Process Vector ranks
        for rank, (chunk, score) in enumerate(vector_results):
            cid = chunk["chunk_id"]
            chunk_dict[cid] = chunk
            vector_scores[cid] = score
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank + 1)

        max_rrf = max(rrf_scores.values()) if rrf_scores else 1.0

        candidates = []
        for cid, chunk in chunk_dict.items():
            rrf_raw = rrf_scores[cid]
            rrf_norm = rrf_raw / max_rrf if max_rrf > 0 else 0.0
            
            authority_score = float(chunk.get("authority_score", 1.0))
            
            candidates.append({
                "chunk": chunk,
                "bm25_score": bm25_scores.get(cid, 0.0),
                "vector_score": vector_scores.get(cid, 0.0),
                "rrf_score": rrf_norm,
                "authority_score": authority_score,
                "final_score": rrf_norm * 0.7 + authority_score * 0.3
            })

        # Sort by initial hybrid score
        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return candidates
