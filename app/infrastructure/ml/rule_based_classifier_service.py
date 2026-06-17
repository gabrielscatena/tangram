from __future__ import annotations

from app.domain.entities import ClassificationResult, RetrievedContext, StudentResponse
from app.domain.enums import ConceptualLabel


class RuleBasedClassifierService:
    """Transparent rule-based classifier for the mock.

    The goal is not predictive performance. The goal is to provide a deterministic,
    explainable baseline that can be traced, tested, and replaced by a real model.
    """

    MODEL_VERSION = "rule_based_financial_literacy_v0.1"

    POSITIVE_KEYWORDS = {
        "guardar",
        "poupar",
        "economizar",
        "planejar",
        "necessário",
        "necessario",
        "orçamento",
        "orcamento",
        "investir",
        "juros",
        "comparar",
        "priorizar",
        "futuro",
        "reserva",
    }
    MISCONCEPTION_KEYWORDS = {
        "tudo",
        "sempre gastar",
        "comprar tudo",
        "não precisa guardar",
        "nao precisa guardar",
    }
    VAGUE_KEYWORDS = {"não sei", "nao sei", "talvez", "depende", "normal", "legal"}

    def classify(self, response: StudentResponse, context: list[RetrievedContext]) -> ClassificationResult:
        """Classify a response with deterministic pedagogical rules.

        Args:
            response: Student response.
            context: Retrieved rubrics/examples.

        Returns:
            Classification result.
        """
        text = response.clean_text.lower()
        token_count = len(text.split())
        positive_hits = sum(1 for keyword in self.POSITIVE_KEYWORDS if keyword in text)
        misconception_hits = sum(1 for keyword in self.MISCONCEPTION_KEYWORDS if keyword in text)
        vague_hits = sum(1 for keyword in self.VAGUE_KEYWORDS if keyword in text)
        max_similarity = max((item.similarity for item in context), default=0.0)

        if token_count < 4 or vague_hits > 0:
            label = ConceptualLabel.VAGUE
            confidence = 0.58 if token_count >= 4 else 0.48
            rationale = "Resposta curta ou vaga, com poucos elementos avaliáveis."
        elif misconception_hits > 0 and positive_hits == 0:
            label = ConceptualLabel.INCORRECT
            confidence = 0.75
            rationale = "Resposta contém possível concepção equivocada sem justificativa financeira adequada."
        elif positive_hits >= 2 and max_similarity >= 0.05:
            label = ConceptualLabel.CORRECT
            confidence = min(0.92, 0.70 + 0.05 * positive_hits + max_similarity)
            rationale = "Resposta apresenta conceitos financeiros relevantes e justificativa coerente."
        elif positive_hits >= 1:
            label = ConceptualLabel.PARTIALLY_CORRECT
            confidence = min(0.82, 0.62 + 0.05 * positive_hits + max_similarity)
            rationale = "Resposta menciona conceito financeiro relevante, mas poderia justificar melhor."
        else:
            label = ConceptualLabel.INCORRECT
            confidence = 0.55
            rationale = "Resposta não evidencia os conceitos esperados na rubrica recuperada."

        confidence = round(float(confidence), 4)
        probabilities = self._probabilities(label, confidence)
        clarity_score = round(min(1.0, max(0.1, token_count / 28)), 4)
        structure_score = round(min(1.0, max(0.1, (token_count + positive_hits * 4) / 34)), 4)

        return ClassificationResult(
            conceptual_label=label,
            class_probabilities=probabilities,
            clarity_score=clarity_score,
            structure_score=structure_score,
            confidence_score=confidence,
            model_version=self.MODEL_VERSION,
            rationale=rationale,
        )

    @staticmethod
    def _probabilities(label: ConceptualLabel, confidence: float) -> dict[str, float]:
        labels = [item.value for item in ConceptualLabel]
        remainder = max(0.0, 1.0 - confidence)
        base = remainder / (len(labels) - 1)
        probs = {item: round(base, 4) for item in labels}
        probs[label.value] = round(confidence, 4)
        return probs
