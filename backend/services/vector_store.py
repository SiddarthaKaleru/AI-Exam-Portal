"""FAISS vector store service with sentence-transformers embeddings."""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load embedding model (small and fast)
_model = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


class VectorStore:
    """FAISS-based vector store for document chunks."""

    def __init__(self):
        self.index = None
        self.chunks = []
        self.embeddings = None

    def build_index(self, chunks: list[str]):
        """Build FAISS index from text chunks."""
        model = _get_model()
        self.chunks = chunks

        # Generate embeddings
        self.embeddings = model.encode(chunks, show_progress_bar=False)
        self.embeddings = np.array(self.embeddings, dtype="float32")

        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

        return self

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for most similar chunks to a query."""
        if self.index is None:
            return []

        model = _get_model()
        query_embedding = model.encode([query])
        query_embedding = np.array(query_embedding, dtype="float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append({
                    "chunk": self.chunks[idx],
                    "score": float(distances[0][i]),
                    "index": int(idx),
                })
        return results


# Global store instance (per-exam stores would be created dynamically)
_stores: dict[str, VectorStore] = {}


def create_store(store_id: str, chunks: list[str]) -> VectorStore:
    """Create and cache a vector store for given chunks."""
    store = VectorStore()
    store.build_index(chunks)
    _stores[store_id] = store
    return store


def get_store(store_id: str) -> VectorStore | None:
    """Retrieve a cached vector store."""
    return _stores.get(store_id)


def search_store(store_id: str, query: str, top_k: int = 5) -> list[dict]:
    """Search a cached vector store."""
    store = get_store(store_id)
    if store is None:
        return []
    return store.search(query, top_k)
