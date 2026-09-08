from typing import List, Dict, Any
import numpy as np
from backend.app.core.config import settings


class Reranker:
    def __init__(self):
        self._model = None
        self._init_model()

    def _init_model(self):
        # Default to high-performance lexical/semantic term overlap cross-scoring for instant response
        self._model = None

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 30) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        top_candidates = candidates[:top_n]
        pairs = [(query, c["chunk"]["raw_text"]) for c in top_candidates]

        if self._model:
            try:
                scores = self._model.predict(pairs)
                # Normalize cross-encoder logits via sigmoid
                scores = 1.0 / (1.0 + np.exp(-scores))
                for i, c in enumerate(top_candidates):
                    c["rerank_score"] = float(scores[i])
                    c["final_score"] = (
                        0.45 * c["rrf_score"]
                        + 0.25 * c["rerank_score"]
                        + 0.15 * c["authority_score"]
                        + 0.15 * c["bm25_score"]
                    )
            except Exception:
                self._fallback_rerank(query, top_candidates)
        else:
            self._fallback_rerank(query, top_candidates)

        top_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return top_candidates

    def _fallback_rerank(self, query: str, candidates: List[Dict[str, Any]]):
        q_words = set(query.lower().split())
        for c in candidates:
            text_words = set(c["chunk"]["normalized_text"].split())
            overlap = len(q_words.intersection(text_words)) / max(len(q_words), 1)
            c["rerank_score"] = float(overlap)
            c["final_score"] = (
                0.45 * c["rrf_score"]
                + 0.25 * c["rerank_score"]
                + 0.15 * c["authority_score"]
                + 0.15 * c["bm25_score"]
            )


reranker = Reranker()
