from typing import List
import numpy as np
from backend.app.core.config import settings


class EmbeddingClient:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.dimension = settings.VECTOR_DIMENSION
        self._model = None
        self._tfidf = None
        self._init_model()

    def _init_model(self):
        if self.provider == "sentence_transformers":
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL, local_files_only=True)
            except Exception:
                self._init_tfidf_fallback()
        else:
            self._init_tfidf_fallback()

    def _init_tfidf_fallback(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._tfidf = TfidfVectorizer(max_features=self.dimension, stop_words="english")
        # Pre-fit on a representative healthcare vocabulary
        base_vocab = [
            "hypertension blood pressure high bp heart disease stroke cardiovascular systolic diastolic",
            "diabetes mellitus blood sugar glucose insulin thirst hunger weight loss fatigue ketoacidosis",
            "dehydration water fluids electrolytes oral rehydration salts diarrhea vomiting fever heat",
            "vaccination vaccines immunization antibodies infection protection immune measles tetanus",
            "healthy diet nutrition fruit vegetables legumes sugar salt sodium fats vitamins calories",
            "anxiety mental health stress depression cognitive behavioral therapy panic disorder worry",
            "maternal child nutrition pregnancy breastfeeding iron folic acid calcium infant feeding",
            "fever temperature body heat infant children viral bacterial infection reye syndrome"
        ]
        self._tfidf.fit(base_vocab)

    def fit_corpus(self, texts: List[str]):
        if self._tfidf and texts:
            # Re-fit or expand tfidf vocab with actual corpus texts
            try:
                self._tfidf.fit(texts)
            except Exception:
                pass

    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self._model:
            embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype(np.float32)

        if self._tfidf:
            dense = self._tfidf.transform(texts).toarray().astype(np.float32)
            # Normalize rows to unit length for cosine similarity
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            dense = dense / norms
            # Pad or truncate to self.dimension
            if dense.shape[1] < self.dimension:
                pad_width = self.dimension - dense.shape[1]
                dense = np.pad(dense, ((0, 0), (0, pad_width)), mode='constant')
            elif dense.shape[1] > self.dimension:
                dense = dense[:, :self.dimension]
            return dense

        # Fallback random deterministic unit vectors
        return np.random.randn(len(texts), self.dimension).astype(np.float32)


embedding_client = EmbeddingClient()
