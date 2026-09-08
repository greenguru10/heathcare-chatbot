from typing import List, Dict, Any, Tuple
import numpy as np
from backend.app.retrieval.embeddings import embedding_client


class VectorStore:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vectors: np.ndarray = np.empty((0, 384), dtype=np.float32)

    def index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        if not chunks:
            self.vectors = np.empty((0, 384), dtype=np.float32)
            return

        texts = [c["normalized_text"] for c in chunks]
        embedding_client.fit_corpus(texts)
        self.vectors = embedding_client.encode(texts)

    def search(self, query: str, top_k: int = 40) -> List[Tuple[Dict[str, Any], float]]:
        if len(self.chunks) == 0 or self.vectors.shape[0] == 0:
            return []

        query_vec = embedding_client.encode([query])[0]
        # Compute cosine similarity: query_vec . vectors^T
        scores = np.dot(self.vectors, query_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.0:
                results.append((self.chunks[idx], score))

        return results
