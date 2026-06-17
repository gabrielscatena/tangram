from __future__ import annotations

from typing import Protocol

from app.domain.entities import (
    AmbiguityResult,
    ClassificationResult,
    FeedbackResult,
    HumanReview,
    KnowledgeDocument,
    RetrievedContext,
    Rubric,
    StudentResponse,
    TraceStep,
)


class ResponseRepository(Protocol):
    """Persistence contract for student responses."""

    def save_response(self, response: StudentResponse) -> None:
        """Persist a student response."""

    def get_response(self, response_id: str) -> StudentResponse | None:
        """Return a response by id."""

    def list_pending_review(self) -> list[StudentResponse]:
        """List responses pending human review."""

    def mark_pending_review(self, response_id: str) -> None:
        """Mark response as requiring human review."""


class RubricRepository(Protocol):
    """Persistence contract for rubrics."""

    def list_rubrics(self) -> list[Rubric]:
        """Return available rubrics."""

    def get_by_question(self, question_id: str) -> list[Rubric]:
        """Return rubrics for a question."""


class HumanReviewRepository(Protocol):
    """Persistence contract for human reviews."""

    def save_review(self, review: HumanReview) -> None:
        """Persist a human review."""


class VectorRetriever(Protocol):
    """Retriever contract for vector or semantic search."""

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedContext]:
        """Retrieve semantically relevant context."""


class ResponseClassifier(Protocol):
    """Classifier contract."""

    def classify(self, response: StudentResponse, context: list[RetrievedContext]) -> ClassificationResult:
        """Classify a student response."""


class AmbiguityScorer(Protocol):
    """Ambiguity scoring contract."""

    def score(
        self,
        response: StudentResponse,
        classification: ClassificationResult,
        context: list[RetrievedContext],
    ) -> AmbiguityResult:
        """Calculate ambiguity and human-review routing."""


class FeedbackGenerator(Protocol):
    """Feedback generation contract."""

    def generate(
        self,
        response: StudentResponse,
        classification: ClassificationResult,
        context: list[RetrievedContext],
    ) -> FeedbackResult:
        """Generate feedback from response, labels, and context."""


class TraceService(Protocol):
    """Tracing contract."""

    def start_trace(self, name: str, metadata: dict[str, object]) -> str:
        """Start a trace and return its id."""

    def log_step(
        self,
        trace_id: str,
        response_id: str,
        step_name: str,
        payload: dict[str, object],
        latency_ms: int = 0,
    ) -> None:
        """Log one trace step."""

    def end_trace(self, trace_id: str, output: dict[str, object]) -> None:
        """Finish a trace."""

    def list_steps(self) -> list[TraceStep]:
        """Return locally available trace steps."""
