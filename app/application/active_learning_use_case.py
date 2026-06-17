from __future__ import annotations

from dataclasses import dataclass

from app.domain.contracts import ResponseRepository


@dataclass(frozen=True)
class ActiveLearningCandidate:
    """A response selected for annotation."""

    response_id: str
    priority: float
    reason: str


class ActiveLearningUseCase:
    """Select responses for human annotation.

    This mock implementation prioritizes responses already routed to review. A production
    implementation would combine uncertainty, diversity, fairness strata, and business priorities.
    """

    def __init__(self, response_repository: ResponseRepository) -> None:
        self._response_repository = response_repository

    def list_candidates(self) -> list[ActiveLearningCandidate]:
        """Return annotation candidates.

        Returns:
            Candidate list sorted by mock priority.
        """
        responses = self._response_repository.list_pending_review()
        return [
            ActiveLearningCandidate(
                response_id=response.response_id,
                priority=1.0,
                reason="Resposta encaminhada para human-in-the-loop por ambiguidade/incerteza.",
            )
            for response in responses
        ]
