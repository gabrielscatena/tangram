from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.enums import ConceptualLabel, GenerationStrategy, HumanReviewStatus


def utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class StudentResponse:
    """A student free-text answer after privacy controls.

    The question metadata fields are optional to keep backwards compatibility with
    earlier mock tests and API payloads. When provided, they are used to build a
    richer RAG query and to make feedback/trace output more auditable.
    """

    response_id: str
    pseudo_student_id: str
    question_id: str
    raw_text: str
    clean_text: str
    grade_level: str
    question_title: str = ""
    question_prompt: str = ""
    financial_topic: str = ""
    bncc_skill: str = ""
    bloom_level: str = ""
    difficulty: str = ""
    expected_answer: str = ""
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class Question:
    """Question-bank entry used by the student playground and API.

    Args:
        question_id: Stable question identifier.
        title: Short display title.
        prompt: Discursive prompt shown to the student.
        grade_level: Target school grade/year.
        financial_topic: Main financial education topic.
        bncc_area: Curricular area alignment label.
        bncc_skill: BNCC anchor. In this mock, values may be demonstrative.
        bloom_level: Bloom taxonomy level.
        difficulty: Difficulty bucket: facil, medio, dificil.
        expected_answer: Expected answer description.
        rubric_conceptual: Conceptual rubric.
        rubric_clarity: Clarity rubric.
        rubric_structure: Structure rubric.
    """

    question_id: str
    title: str
    prompt: str
    grade_level: str
    financial_topic: str
    bncc_area: str
    bncc_skill: str
    bloom_level: str
    difficulty: str
    expected_answer: str
    rubric_conceptual: str
    rubric_clarity: str
    rubric_structure: str


@dataclass(frozen=True)
class Rubric:
    """Pedagogical rubric aligned to a question/topic."""

    rubric_id: str
    question_id: str
    bncc_skill: str
    bloom_level: str
    financial_topic: str
    criterion: str
    expected_concept: str
    partial_concept: str
    misconception: str
    version: str = "v0.1"


@dataclass(frozen=True)
class KnowledgeDocument:
    """Small knowledge-base document indexed by the demo vector retriever.

    The mock uses curated snippets and, in v4/v5, can also use vector artifacts
    built from original PDFs. In a real project, this entity would point to
    validated curricular source documents, versioned PDFs, rubrics, teacher
    guides, examples and policy notes.
    """

    document_id: str
    source_type: str
    title: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)
    version: str = "v0.1"


@dataclass(frozen=True)
class RetrievedContext:
    """A retrieved rubric/example/source chunk used as context."""

    context_id: str
    text: str
    source_type: str
    similarity: float
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ClassificationResult:
    """Output from a pedagogical classifier."""

    conceptual_label: ConceptualLabel
    class_probabilities: dict[str, float]
    clarity_score: float
    structure_score: float
    confidence_score: float
    model_version: str
    rationale: str


@dataclass(frozen=True)
class AmbiguityResult:
    """Ambiguity and uncertainty assessment."""

    ambiguity_score: float
    human_review_required: bool
    reasons: list[str]


@dataclass(frozen=True)
class FeedbackResult:
    """Generated formative feedback."""

    feedback_text: str
    generation_strategy: GenerationStrategy
    template_id: str
    safety_flags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationResult:
    """Full result returned to the app/API."""

    response: StudentResponse
    classification: ClassificationResult
    ambiguity: AmbiguityResult
    feedback: FeedbackResult
    retrieved_context: list[RetrievedContext]
    trace_id: str
    human_review_status: HumanReviewStatus


@dataclass(frozen=True)
class HumanReview:
    """A review performed by a teacher or specialist."""

    review_id: str
    response_id: str
    reviewer_role: str
    corrected_label: ConceptualLabel
    edited_feedback: str
    decision: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class TraceStep:
    """Single trace step persisted locally."""

    trace_id: str
    response_id: str
    step_name: str
    payload: dict[str, object]
    latency_ms: int
    created_at: datetime = field(default_factory=utc_now)
