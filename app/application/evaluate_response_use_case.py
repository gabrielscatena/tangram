from __future__ import annotations

import logging
import time
import uuid

from app.domain.contracts import (
    AmbiguityScorer,
    FeedbackGenerator,
    ResponseClassifier,
    ResponseRepository,
    TraceService,
    VectorRetriever,
)
from app.domain.entities import EvaluationResult, StudentResponse
from app.domain.enums import HumanReviewStatus
from app.domain.exceptions import InvalidStudentResponseError
from app.domain.value_objects import EvaluationRequest
from app.infrastructure.privacy.pii_redactor import PIIRedactor
from app.infrastructure.privacy.pseudonymizer import Pseudonymizer
from app.infrastructure.preprocessing.text_preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


class EvaluateResponseUseCase:
    """Evaluate a student answer and generate a pedagogical feedback decision."""

    def __init__(
        self,
        response_repository: ResponseRepository,
        vector_retriever: VectorRetriever,
        classifier: ResponseClassifier,
        ambiguity_scorer: AmbiguityScorer,
        feedback_generator: FeedbackGenerator,
        trace_service: TraceService,
        pseudonymizer: Pseudonymizer,
        pii_redactor: PIIRedactor,
        preprocessor: TextPreprocessor,
    ) -> None:
        self._response_repository = response_repository
        self._vector_retriever = vector_retriever
        self._classifier = classifier
        self._ambiguity_scorer = ambiguity_scorer
        self._feedback_generator = feedback_generator
        self._trace_service = trace_service
        self._pseudonymizer = pseudonymizer
        self._pii_redactor = pii_redactor
        self._preprocessor = preprocessor

    def execute(self, request: EvaluationRequest) -> EvaluationResult:
        """Run the full mock evaluation pipeline.

        Args:
            request: Student response evaluation request.

        Returns:
            Full evaluation result including classification, ambiguity, feedback, and trace.

        Raises:
            InvalidStudentResponseError: If the answer is empty or too large.
        """
        if not request.raw_text or not request.raw_text.strip():
            raise InvalidStudentResponseError("Student response cannot be empty.")
        if len(request.raw_text) > 5000:
            raise InvalidStudentResponseError("Student response is too long for this mock.")

        response_id = f"resp_{uuid.uuid4().hex[:12]}"
        pseudo_student_id = self._pseudonymizer.pseudonymize(request.student_id)
        trace_id = self._trace_service.start_trace(
            "evaluate_student_response",
            {"response_id": response_id, "question_id": request.question_id},
        )

        start = time.perf_counter()
        redacted = self._pii_redactor.redact(request.raw_text)
        clean_text = self._preprocessor.clean(redacted)
        response = StudentResponse(
            response_id=response_id,
            pseudo_student_id=pseudo_student_id,
            question_id=request.question_id,
            raw_text=redacted,
            clean_text=clean_text,
            grade_level=request.grade_level,
            question_title=request.question_title,
            question_prompt=request.question_prompt,
            financial_topic=request.financial_topic,
            bncc_skill=request.bncc_skill,
            bloom_level=request.bloom_level,
            difficulty=request.difficulty,
            expected_answer=request.expected_answer,
        )
        self._response_repository.save_response(response)
        self._trace_service.log_step(
            trace_id,
            response_id,
            "privacy_and_preprocessing",
            {
                "clean_text": clean_text,
                "pseudo_student_id": pseudo_student_id,
                "student_id_strategy": "pseudonymized",
                "pii_redacted": redacted != request.raw_text,
                "question_id": request.question_id,
                "question_title": request.question_title,
                "question_prompt": request.question_prompt,
                "financial_topic": request.financial_topic,
                "bncc_skill": request.bncc_skill,
                "bloom_level": request.bloom_level,
                "difficulty": request.difficulty,
            },
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

        start = time.perf_counter()
        retrieval_query = self._build_retrieval_query(request, clean_text)
        context = self._vector_retriever.retrieve(retrieval_query, top_k=5)
        self._trace_service.log_step(
            trace_id,
            response_id,
            "semantic_retrieval",
            {
                "retrieval_query": retrieval_query,
                "top_k": len(context),
                "contexts": [
                    {
                        "context_id": item.context_id,
                        "source_type": item.source_type,
                        "similarity": item.similarity,
                        "metadata": item.metadata,
                        "preview": item.text[:500],
                    }
                    for item in context
                ],
            },
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

        start = time.perf_counter()
        classification = self._classifier.classify(response, context)
        self._trace_service.log_step(
            trace_id,
            response_id,
            "classification",
            {
                "label": classification.conceptual_label.value,
                "confidence": classification.confidence_score,
                "rationale": classification.rationale,
            },
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

        start = time.perf_counter()
        ambiguity = self._ambiguity_scorer.score(response, classification, context)
        self._trace_service.log_step(
            trace_id,
            response_id,
            "ambiguity_scoring",
            {
                "ambiguity_score": ambiguity.ambiguity_score,
                "human_review_required": ambiguity.human_review_required,
                "reasons": ambiguity.reasons,
            },
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

        start = time.perf_counter()
        feedback = self._feedback_generator.generate(response, classification, context)
        self._trace_service.log_step(
            trace_id,
            response_id,
            "feedback_generation",
            {
                "strategy": feedback.generation_strategy.value,
                "template_id": feedback.template_id,
                "safety_flags": feedback.safety_flags,
            },
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

        if ambiguity.human_review_required:
            self._response_repository.mark_pending_review(response_id)
            human_review_status = HumanReviewStatus.REQUIRED
        else:
            human_review_status = HumanReviewStatus.NOT_REQUIRED

        self._trace_service.end_trace(
            trace_id,
            {
                "response_id": response_id,
                "human_review_status": human_review_status.value,
                "feedback_preview": feedback.feedback_text[:120],
            },
        )

        logger.info(
            "response_evaluated",
            extra={
                "response_id": response_id,
                "trace_id": trace_id,
                "confidence_score": classification.confidence_score,
                "ambiguity_score": ambiguity.ambiguity_score,
                "human_review_required": ambiguity.human_review_required,
            },
        )

        return EvaluationResult(
            response=response,
            classification=classification,
            ambiguity=ambiguity,
            feedback=feedback,
            retrieved_context=context,
            trace_id=trace_id,
            human_review_status=human_review_status,
        )


    @staticmethod
    def _build_retrieval_query(request: EvaluationRequest, clean_text: str) -> str:
        """Build a context-rich query for source retrieval.

        Args:
            request: Evaluation request with question metadata.
            clean_text: Preprocessed student answer.

        Returns:
            Query text that joins question, expected concept and answer.
        """
        parts = [
            request.question_title,
            request.question_prompt,
            request.financial_topic.replace("_", " "),
            request.bncc_skill,
            request.bloom_level,
            request.expected_answer,
            clean_text,
        ]
        return " ".join(part for part in parts if part and part.strip())
