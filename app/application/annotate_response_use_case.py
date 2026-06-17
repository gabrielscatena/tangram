from __future__ import annotations

import uuid

from app.domain.contracts import HumanReviewRepository
from app.domain.entities import HumanReview
from app.domain.enums import ConceptualLabel, ReviewDecision
from app.domain.value_objects import ReviewRequest


class AnnotateResponseUseCase:
    """Persist a human review for active learning and quality control."""

    def __init__(self, human_review_repository: HumanReviewRepository) -> None:
        self._human_review_repository = human_review_repository

    def execute(self, request: ReviewRequest) -> HumanReview:
        """Save a review decision.

        Args:
            request: Human review request.

        Returns:
            Persisted human review entity.
        """
        corrected_label = ConceptualLabel(request.corrected_label)
        decision = ReviewDecision(request.decision)
        review = HumanReview(
            review_id=f"review_{uuid.uuid4().hex[:12]}",
            response_id=request.response_id,
            reviewer_role=request.reviewer_role,
            corrected_label=corrected_label,
            edited_feedback=request.edited_feedback,
            decision=decision.value,
        )
        self._human_review_repository.save_review(review)
        return review
