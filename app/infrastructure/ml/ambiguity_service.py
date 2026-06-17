from __future__ import annotations

import math

from app.domain.entities import AmbiguityResult, ClassificationResult, RetrievedContext, StudentResponse


class EntropyAmbiguityScorer:
    """Calculate a combined ambiguity/uncertainty score."""

    def __init__(self, review_threshold: float = 0.58) -> None:
        self._review_threshold = review_threshold

    def score(
        self,
        response: StudentResponse,
        classification: ClassificationResult,
        context: list[RetrievedContext],
    ) -> AmbiguityResult:
        """Calculate ambiguity and decide whether human review is required.

        Args:
            response: Student response.
            classification: Classifier output.
            context: Retrieved context.

        Returns:
            Ambiguity result with reasons.
        """
        entropy_score = self._normalized_entropy(classification.class_probabilities)
        top_margin_penalty = self._top_margin_penalty(classification.class_probabilities)
        max_similarity = max((item.similarity for item in context), default=0.0)
        low_similarity_penalty = max(0.0, 1.0 - min(max_similarity / 0.25, 1.0))
        token_count = len(response.clean_text.split())
        short_penalty = 1.0 if token_count < 5 else max(0.0, 1.0 - token_count / 20)

        score = (
            0.40 * entropy_score
            + 0.25 * low_similarity_penalty
            + 0.20 * short_penalty
            + 0.15 * top_margin_penalty
        )
        score = round(min(1.0, max(0.0, score)), 4)
        reasons = self._build_reasons(
            entropy_score=entropy_score,
            low_similarity_penalty=low_similarity_penalty,
            short_penalty=short_penalty,
            top_margin_penalty=top_margin_penalty,
            confidence=classification.confidence_score,
        )
        human_review_required = score >= self._review_threshold or classification.confidence_score < 0.60
        return AmbiguityResult(
            ambiguity_score=score,
            human_review_required=human_review_required,
            reasons=reasons,
        )

    @staticmethod
    def _normalized_entropy(probabilities: dict[str, float]) -> float:
        values = [max(0.0, min(1.0, value)) for value in probabilities.values() if value > 0]
        if not values:
            return 1.0
        entropy = -sum(value * math.log(value) for value in values)
        max_entropy = math.log(len(probabilities)) if len(probabilities) > 1 else 1.0
        return round(entropy / max_entropy, 4)

    @staticmethod
    def _top_margin_penalty(probabilities: dict[str, float]) -> float:
        values = sorted(probabilities.values(), reverse=True)
        if len(values) < 2:
            return 0.0
        margin = values[0] - values[1]
        return round(max(0.0, 1.0 - margin), 4)

    @staticmethod
    def _build_reasons(
        entropy_score: float,
        low_similarity_penalty: float,
        short_penalty: float,
        top_margin_penalty: float,
        confidence: float,
    ) -> list[str]:
        reasons: list[str] = []
        if entropy_score > 0.65:
            reasons.append("Distribuição de classes pouco concentrada.")
        if low_similarity_penalty > 0.70:
            reasons.append("Baixa similaridade com rubricas/exemplos conhecidos.")
        if short_penalty > 0.70:
            reasons.append("Resposta muito curta ou pouco desenvolvida.")
        if top_margin_penalty > 0.65:
            reasons.append("Margem pequena entre as classes mais prováveis.")
        if confidence < 0.60:
            reasons.append("Confiança do classificador abaixo do mínimo recomendado.")
        return reasons or ["Ambiguidade dentro do intervalo esperado para feedback automático."]
