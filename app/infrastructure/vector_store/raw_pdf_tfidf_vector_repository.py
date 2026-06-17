from __future__ import annotations

from pathlib import Path

from app.domain.entities import RetrievedContext
from app.domain.contracts import VectorRetriever
from app.infrastructure.knowledge.raw_pdf_pipeline import read_chunks_jsonl


class RawPdfTfidfVectorRepository(VectorRetriever):
    """Retriever backed by the TF-IDF artifacts built from original PDFs.

    Expected artifacts under vector_dir:
    - tfidf_vectorizer.joblib
    - tfidf_matrix.npz
    - indexed_chunks.jsonl

    This class intentionally keeps the same VectorRetriever contract used by the
    demo app so it can replace the synthetic in-memory retriever when artifacts
    exist.
    """

    def __init__(self, vector_dir: Path = Path("data/vector_store")) -> None:
        self._vector_dir = vector_dir
        self._vectorizer_path = vector_dir / "tfidf_vectorizer.joblib"
        self._matrix_path = vector_dir / "tfidf_matrix.npz"
        self._chunks_path = vector_dir / "indexed_chunks.jsonl"
        self._vectorizer = None
        self._matrix = None
        self._chunks = []
        self._load()

    @classmethod
    def artifacts_exist(cls, vector_dir: Path = Path("data/vector_store")) -> bool:
        """Return True when the raw PDF vector artifacts are available."""
        return all(
            (vector_dir / name).exists()
            for name in ["tfidf_vectorizer.joblib", "tfidf_matrix.npz", "indexed_chunks.jsonl"]
        )

    def _load(self) -> None:
        try:
            import joblib
            from scipy import sparse
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Raw PDF vector retrieval requires joblib, scipy and scikit-learn.") from exc

        if not self.artifacts_exist(self._vector_dir):
            raise FileNotFoundError(
                "Raw PDF vector artifacts not found. Run scripts/build_raw_pdf_vector_db.py first."
            )
        self._vectorizer = joblib.load(self._vectorizer_path)
        self._matrix = sparse.load_npz(self._matrix_path)
        self._chunks = read_chunks_jsonl(self._chunks_path)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedContext]:
        """Retrieve top-k original-source chunks for a query.

        Args:
            query: Context-rich query built from question metadata and student answer.
            top_k: Number of chunks to return.

        Returns:
            Retrieved contexts with source path, page and preview metadata.
        """
        if self._vectorizer is None or self._matrix is None:
            return []
        from sklearn.metrics.pairwise import cosine_similarity

        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix).flatten()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:top_k]
        contexts: list[RetrievedContext] = []
        for idx, score in ranked:
            chunk = self._chunks[idx]
            contexts.append(
                RetrievedContext(
                    context_id=chunk.chunk_id,
                    text=chunk.text,
                    source_type="raw_pdf_chunk",
                    similarity=round(float(score), 4),
                    metadata={
                        "source_id": chunk.source_id,
                        "source_path": chunk.source_path,
                        "source_sha256": chunk.source_sha256,
                        "page_number": str(chunk.page_number),
                        "chunk_index": str(chunk.chunk_index),
                        "chunking_version": chunk.chunking_version,
                    },
                )
            )
        return contexts
