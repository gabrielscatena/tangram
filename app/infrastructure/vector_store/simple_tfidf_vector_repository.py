from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities import KnowledgeDocument, RetrievedContext, Rubric


@dataclass(frozen=True)
class _VectorEntry:
    """Internal text entry indexed by the lightweight retriever."""

    context_id: str
    text: str
    source_type: str
    metadata: dict[str, str]


class SimpleTfidfVectorRepository:
    """Lightweight semantic-ish retriever using scikit-learn TF-IDF.

    This class is intentionally simple to keep the mock runnable in CPU-only local
    environments. It indexes both pedagogical rubrics and small knowledge documents
    such as BNCC/Bloom seed snippets. It can be replaced by Chroma, FAISS, pgvector,
    or another vector DB.
    """

    def __init__(self, rubrics: list[Rubric], documents: list[KnowledgeDocument] | None = None) -> None:
        self._entries = self._build_entries(rubrics, documents or [])
        self._texts = [entry.text for entry in self._entries]
        self._vectorizer = None
        self._matrix = None
        self._fit()

    def _fit(self) -> None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError:  # pragma: no cover - fallback path
            self._vectorizer = None
            self._matrix = None
            return
        self._vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform(self._texts) if self._texts else None

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedContext]:
        """Retrieve top-k rubrics/documents for a response.

        Args:
            query: Student response text.
            top_k: Number of contexts to return.

        Returns:
            Retrieved contexts sorted by similarity descending.
        """
        if not self._entries:
            return []
        if self._vectorizer is None or self._matrix is None:
            return self._keyword_fallback(query, top_k)

        from sklearn.metrics.pairwise import cosine_similarity

        query_vector = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self._matrix).flatten()
        ranked = sorted(enumerate(similarities), key=lambda item: item[1], reverse=True)[:top_k]
        return [self._to_context(index, float(score)) for index, score in ranked]

    def _keyword_fallback(self, query: str, top_k: int) -> list[RetrievedContext]:
        query_tokens = set(query.lower().split())
        scored: list[tuple[int, float]] = []
        for idx, text in enumerate(self._texts):
            tokens = set(text.lower().split())
            score = len(query_tokens & tokens) / max(len(query_tokens | tokens), 1)
            scored.append((idx, score))
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
        return [self._to_context(index, score) for index, score in ranked]

    def _to_context(self, index: int, similarity: float) -> RetrievedContext:
        entry = self._entries[index]
        return RetrievedContext(
            context_id=entry.context_id,
            text=entry.text,
            source_type=entry.source_type,
            similarity=round(similarity, 4),
            metadata=entry.metadata,
        )

    @classmethod
    def _build_entries(cls, rubrics: list[Rubric], documents: list[KnowledgeDocument]) -> list[_VectorEntry]:
        entries: list[_VectorEntry] = []
        for rubric in rubrics:
            entries.append(
                _VectorEntry(
                    context_id=rubric.rubric_id,
                    text=cls._rubric_to_text(rubric),
                    source_type="rubric",
                    metadata={
                        "question_id": rubric.question_id,
                        "bncc_skill": rubric.bncc_skill,
                        "bloom_level": rubric.bloom_level,
                        "financial_topic": rubric.financial_topic,
                        "version": rubric.version,
                    },
                )
            )
        for document in documents:
            metadata = dict(document.metadata)
            metadata["title"] = document.title
            metadata["version"] = document.version
            entries.append(
                _VectorEntry(
                    context_id=document.document_id,
                    text=f"{document.title} {document.text}",
                    source_type=document.source_type,
                    metadata=metadata,
                )
            )
        return entries

    @staticmethod
    def _rubric_to_text(rubric: Rubric) -> str:
        return " ".join(
            [
                rubric.financial_topic,
                rubric.criterion,
                rubric.expected_concept,
                rubric.partial_concept,
                rubric.misconception,
                rubric.bncc_skill,
                rubric.bloom_level,
            ]
        )
