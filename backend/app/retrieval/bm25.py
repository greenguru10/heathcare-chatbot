import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, k1: float = 1.2, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25: BM25Okapi = None
        self.corpus_chunks: List[Dict[str, Any]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Split into alphanumeric tokens, lowercase
        return re.findall(r"\b\w+\b", text.lower())

    def index(self, chunks: List[Dict[str, Any]]):
        self.corpus_chunks = chunks
        if not chunks:
            self.bm25 = None
            return

        tokenized_corpus = [self._tokenize(c["normalized_text"]) for c in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus, k1=self.k1, b=self.b)

    def search(self, query: str, top_k: int = 40) -> List[Tuple[Dict[str, Any], float]]:
        if not self.bm25 or not self.corpus_chunks:
            return []

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
        for idx in top_indices:
            if scores[idx] > 0:
                normalized_score = float(scores[idx] / max_score)
                results.append((self.corpus_chunks[idx], normalized_score))

        return results
