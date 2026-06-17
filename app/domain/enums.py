from __future__ import annotations

from enum import StrEnum


class ConceptualLabel(StrEnum):
    """Pedagogical label for conceptual correctness."""

    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    VAGUE = "vague"


class HumanReviewStatus(StrEnum):
    """Human review status."""

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    COMPLETED = "completed"


class GenerationStrategy(StrEnum):
    """Feedback generation strategy."""

    TEMPLATE = "template"
    RAG_TEMPLATE = "rag_template"
    LLM_OPTIONAL = "llm_optional"


class ReviewDecision(StrEnum):
    """Possible human review decisions."""

    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"
