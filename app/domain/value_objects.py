from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationRequest:
    """Input to the response evaluation use case.

    Question metadata is optional to preserve API compatibility. When supplied,
    it is concatenated with the student answer to build a richer retrieval query
    against the original-source vector database.
    """

    student_id: str
    question_id: str
    raw_text: str
    grade_level: str = "7_ano"
    question_title: str = ""
    question_prompt: str = ""
    financial_topic: str = ""
    bncc_skill: str = ""
    bloom_level: str = ""
    difficulty: str = ""
    expected_answer: str = ""


@dataclass(frozen=True)
class ReviewRequest:
    """Input to a human review action."""

    response_id: str
    reviewer_role: str
    corrected_label: str
    edited_feedback: str
    decision: str
