from __future__ import annotations

from app.domain.entities import ClassificationResult, FeedbackResult, RetrievedContext, StudentResponse
from app.domain.enums import ConceptualLabel, GenerationStrategy


class TemplateFeedbackGenerator:
    """Generate controlled formative feedback using templates and retrieved sources."""

    def generate(
        self,
        response: StudentResponse,
        classification: ClassificationResult,
        context: list[RetrievedContext],
    ) -> FeedbackResult:
        """Generate feedback from the classification and context.

        Args:
            response: Student response with question metadata.
            classification: Classifier output.
            context: Retrieved context from rubrics or original PDFs.

        Returns:
            Feedback result.
        """
        topic = self._topic_from_response_or_context(response, context)
        label = classification.conceptual_label
        source_hint = self._source_hint(context)

        if label is ConceptualLabel.CORRECT:
            template_id = "tpl_positive_extend_v1"
            text = (
                f"Boa resposta! Você mostrou uma boa compreensão de {topic}. "
                "Para avançar ainda mais, acrescente um exemplo concreto ou explique melhor a consequência da sua decisão."
            )
        elif label is ConceptualLabel.PARTIALLY_CORRECT:
            template_id = "tpl_partial_scaffold_v1"
            text = (
                f"Você começou bem ao tratar de {topic}. "
                "Para melhorar, conecte sua resposta ao planejamento financeiro e explique com mais clareza o critério da sua escolha."
            )
        elif label is ConceptualLabel.VAGUE:
            template_id = "tpl_vague_prompt_v1"
            text = (
                "Sua resposta ainda está um pouco curta. Tente explicar o que você faria, "
                "por que faria essa escolha e como isso ajuda no uso responsável do dinheiro."
            )
        else:
            template_id = "tpl_misconception_repair_v1"
            text = (
                f"Vamos revisar este ponto: em {topic}, é importante justificar a decisão considerando necessidades, "
                "prioridades, riscos e consequências futuras. Tente reescrever sua resposta com uma justificativa mais completa."
            )

        if response.expected_answer:
            text += f" Uma boa resposta deveria se aproximar desta ideia: {response.expected_answer}"
        if source_hint:
            text += f" Contexto recuperado: {source_hint}."

        return FeedbackResult(
            feedback_text=text,
            generation_strategy=GenerationStrategy.RAG_TEMPLATE if context else GenerationStrategy.TEMPLATE,
            template_id=template_id,
            safety_flags=[],
        )

    @staticmethod
    def _topic_from_response_or_context(response: StudentResponse, context: list[RetrievedContext]) -> str:
        if response.financial_topic:
            return response.financial_topic.replace("_", " ")
        if response.question_title:
            return response.question_title
        for item in context:
            topic = item.metadata.get("financial_topic") or item.metadata.get("topic") or item.metadata.get("concept")
            if topic:
                return topic.replace("_", " ")
        return "educação financeira"

    @staticmethod
    def _source_hint(context: list[RetrievedContext]) -> str:
        """Return a compact source hint from retrieved original documents."""
        for item in context:
            source_path = item.metadata.get("source_path")
            page_number = item.metadata.get("page_number")
            if source_path and page_number:
                return f"fonte oficial em {source_path}, página {page_number}"
        return ""
