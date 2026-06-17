from __future__ import annotations

from app.domain.entities import KnowledgeDocument, RetrievedContext, Rubric
from app.infrastructure.vector_store.simple_tfidf_vector_repository import SimpleTfidfVectorRepository


class ChromaVectorRepository:
    """Optional Chroma adapter placeholder with TF-IDF fallback.

    The mock keeps this adapter intentionally conservative. In a real implementation,
    this class would own collection creation, embedding persistence, metadata filters,
    and migration/versioning of vector indexes.
    """

    def __init__(
        self,
        rubrics: list[Rubric],
        documents: list[KnowledgeDocument] | None = None,
        persist_directory: str = "data/vector_store",
    ) -> None:
        self._persist_directory = persist_directory
        self._fallback = SimpleTfidfVectorRepository(rubrics, documents=documents)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedContext]:
        """Retrieve contexts using the available vector backend.

        Args:
            query: Student response text.
            top_k: Number of contexts to return.

        Returns:
            Retrieved contexts.
        """
        return self._fallback.retrieve(query, top_k=top_k)
