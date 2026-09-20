import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from app.models.product import Product

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG pipeline:
    Product Data -> Document Chunks -> Vector Embeddings -> FAISS Index -> Semantic Retrieval.
    Ensures answers to technical and comparative questions are strictly grounded in catalog data.
    """

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []
        self._is_ready = False

    def build_index(self, products: List[Product]):
        """Creates semantic chunks from products and builds FAISS vector store index."""
        logger.info("Building FAISS RAG index for %d products...", len(products))
        self.chunks = []

        for p in products:
            # Chunk 1: General overview and tags
            chunk_main = (
                f"Product: {p.name}. Category: {p.category}. Brand: {p.brand}. "
                f"Price: ₹{p.price} (Original MRP: ₹{p.original_price}, Discount: {p.discount_percentage}%). "
                f"Rating: {p.rating}/5 with stock {p.stock}. "
                f"Description: {p.description} "
                f"Tags: {', '.join(p.tags)}."
            )
            self.chunks.append({
                "product_id": p.id,
                "product_name": p.name,
                "category": p.category,
                "price": p.price,
                "chunk_type": "overview",
                "text": chunk_main
            })

            # Chunk 2: Deep features and specifications
            if p.features:
                features_text = "; ".join(p.features)
                chunk_feat = (
                    f"Product {p.name} Specifications and Features: {features_text}. "
                    f"Available Colors: {p.color}. Available Sizes: {', '.join(str(s) for s in p.sizes)}."
                )
                self.chunks.append({
                    "product_id": p.id,
                    "product_name": p.name,
                    "category": p.category,
                    "price": p.price,
                    "chunk_type": "specs",
                    "text": chunk_feat
                })

        # Fit Vectorizer and generate embeddings
        corpus = [c["text"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=2048
        )
        tfidf_matrix = self.vectorizer.fit_transform(corpus).toarray().astype("float32")

        # L2 normalize for cosine similarity via Inner Product
        faiss.normalize_L2(tfidf_matrix)

        dim = tfidf_matrix.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(tfidf_matrix)
        self._is_ready = True
        logger.info("FAISS RAG index successfully built with %d chunks (dim: %d)", len(self.chunks), dim)

    def search(self, query: str, top_k: int = 4, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Performs semantic vector search over FAISS index."""
        if not self._is_ready or not self.vectorizer or not self.index:
            logger.warning("RAG index is not initialized.")
            return []

        q_vec = self.vectorizer.transform([query]).toarray().astype("float32")
        faiss.normalize_L2(q_vec)

        # Retrieve more candidates if category filtering is active
        k_retrieve = min(len(self.chunks), max(top_k * 3, 10))
        distances, indices = self.index.search(q_vec, k_retrieve)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.chunks[idx]
            if category_filter and chunk["category"].lower() != category_filter.lower():
                continue

            results.append({
                "product_id": chunk["product_id"],
                "product_name": chunk["product_name"],
                "category": chunk["category"],
                "price": chunk["price"],
                "text": chunk["text"],
                "score": float(dist)
            })
            if len(results) >= top_k:
                break

        return results

    def get_grounded_context_string(self, query: str, top_k: int = 4) -> str:
        """Retrieves and formats top chunks for LLM RAG prompt injection."""
        results = self.search(query, top_k=top_k)
        if not results:
            return "No matching verified specifications found in the catalog."

        lines = ["VERIFIED CATALOG SPECIFICATIONS:"]
        for idx, r in enumerate(results, 1):
            lines.append(f"[{idx}] {r['product_name']} (₹{r['price']:,}): {r['text']}")
        return "\n".join(lines)

rag_service = RAGService()
