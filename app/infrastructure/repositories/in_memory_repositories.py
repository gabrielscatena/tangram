from __future__ import annotations

from app.domain.entities import HumanReview, Rubric, StudentResponse, TraceStep


class InMemoryResponseRepository:
    """In-memory repository for responses used in tests and demo mode."""

    def __init__(self) -> None:
        self._responses: dict[str, StudentResponse] = {}
        self._pending_review: set[str] = set()

    def save_response(self, response: StudentResponse) -> None:
        """Persist response in memory."""
        self._responses[response.response_id] = response

    def get_response(self, response_id: str) -> StudentResponse | None:
        """Get response by id."""
        return self._responses.get(response_id)

    def list_pending_review(self) -> list[StudentResponse]:
        """List responses marked for human review."""
        return [self._responses[item] for item in self._pending_review if item in self._responses]

    def mark_pending_review(self, response_id: str) -> None:
        """Mark response as pending human review."""
        self._pending_review.add(response_id)


class InMemoryRubricRepository:
    """In-memory rubric repository."""

    def __init__(self, rubrics: list[Rubric]) -> None:
        self._rubrics = rubrics

    def list_rubrics(self) -> list[Rubric]:
        """Return all rubrics."""
        return list(self._rubrics)

    def get_by_question(self, question_id: str) -> list[Rubric]:
        """Return rubrics by question id."""
        return [rubric for rubric in self._rubrics if rubric.question_id == question_id]


class InMemoryHumanReviewRepository:
    """In-memory human review repository."""

    def __init__(self) -> None:
        self._reviews: dict[str, HumanReview] = {}

    def save_review(self, review: HumanReview) -> None:
        """Persist review in memory."""
        self._reviews[review.review_id] = review

    def list_reviews(self) -> list[HumanReview]:
        """Return reviews."""
        return list(self._reviews.values())


class InMemoryTraceRepository:
    """In-memory trace step repository."""

    def __init__(self) -> None:
        self._steps: list[TraceStep] = []

    def save_step(self, step: TraceStep) -> None:
        """Persist a trace step."""
        self._steps.append(step)

    def list_steps(self) -> list[TraceStep]:
        """Return trace steps."""
        return list(self._steps)
