from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.application.active_learning_use_case import ActiveLearningUseCase
from app.application.annotate_response_use_case import AnnotateResponseUseCase
from app.application.evaluate_response_use_case import EvaluateResponseUseCase
from app.domain.contracts import VectorRetriever
from app.domain.entities import KnowledgeDocument, Question, Rubric
from app.infrastructure.knowledge.question_bank_loader import load_question_bank, question_bank_to_rubrics
from app.infrastructure.knowledge.seed_loader import load_knowledge_documents, load_rubrics_from_csv
from app.infrastructure.ml.ambiguity_service import EntropyAmbiguityScorer
from app.infrastructure.ml.feedback_generator import TemplateFeedbackGenerator
from app.infrastructure.ml.model_registry import InMemoryModelRegistry
from app.infrastructure.ml.rule_based_classifier_service import RuleBasedClassifierService
from app.infrastructure.observability.json_trace_service import JsonTraceService
from app.infrastructure.preprocessing.text_preprocessor import TextPreprocessor
from app.infrastructure.privacy.pii_redactor import PIIRedactor
from app.infrastructure.privacy.pseudonymizer import Pseudonymizer
from app.infrastructure.repositories.in_memory_repositories import (
    InMemoryHumanReviewRepository,
    InMemoryResponseRepository,
    InMemoryRubricRepository,
)
from app.infrastructure.vector_store.raw_pdf_tfidf_vector_repository import RawPdfTfidfVectorRepository
from app.infrastructure.vector_store.simple_tfidf_vector_repository import SimpleTfidfVectorRepository


@dataclass
class DemoContainer:
    """Dependency container for the local demo app."""

    evaluate_response: EvaluateResponseUseCase
    annotate_response: AnnotateResponseUseCase
    active_learning: ActiveLearningUseCase
    response_repository: InMemoryResponseRepository
    rubric_repository: InMemoryRubricRepository
    human_review_repository: InMemoryHumanReviewRepository
    trace_service: JsonTraceService
    model_registry: InMemoryModelRegistry
    questions: list[Question]
    vector_backend: str


def build_demo_container() -> DemoContainer:
    """Build a complete in-memory container for local/demo use.

    The app now prefers the raw PDF vector database when it exists. If the user
    has not run scripts/build_raw_pdf_vector_db.py yet, the app falls back to the
    older synthetic seed retriever so the UI still opens.
    """
    questions = load_question_bank()
    rubrics = build_seed_rubrics(questions)
    knowledge_documents = build_seed_knowledge_documents()
    response_repository = InMemoryResponseRepository()
    rubric_repository = InMemoryRubricRepository(rubrics)
    human_review_repository = InMemoryHumanReviewRepository()
    trace_service = JsonTraceService(trace_path="data/duckdb/traces.jsonl")
    vector_retriever, vector_backend = build_vector_retriever(rubrics, knowledge_documents)

    evaluate_response = EvaluateResponseUseCase(
        response_repository=response_repository,
        vector_retriever=vector_retriever,
        classifier=RuleBasedClassifierService(),
        ambiguity_scorer=EntropyAmbiguityScorer(review_threshold=0.58),
        feedback_generator=TemplateFeedbackGenerator(),
        trace_service=trace_service,
        pseudonymizer=Pseudonymizer(salt="dev-demo-salt"),
        pii_redactor=PIIRedactor(),
        preprocessor=TextPreprocessor(),
    )
    return DemoContainer(
        evaluate_response=evaluate_response,
        annotate_response=AnnotateResponseUseCase(human_review_repository),
        active_learning=ActiveLearningUseCase(response_repository),
        response_repository=response_repository,
        rubric_repository=rubric_repository,
        human_review_repository=human_review_repository,
        trace_service=trace_service,
        model_registry=InMemoryModelRegistry(),
        questions=questions,
        vector_backend=vector_backend,
    )


def build_vector_retriever(
    rubrics: list[Rubric],
    knowledge_documents: list[KnowledgeDocument],
) -> tuple[VectorRetriever, str]:
    """Build the preferred retriever for the current local state."""
    vector_dir = Path("data/vector_store")
    if RawPdfTfidfVectorRepository.artifacts_exist(vector_dir):
        return RawPdfTfidfVectorRepository(vector_dir), "raw_pdf_tfidf_vector_store"
    return SimpleTfidfVectorRepository(rubrics, documents=knowledge_documents), "seed_tfidf_vector_store"


def build_seed_rubrics(questions: list[Question] | None = None) -> list[Rubric]:
    """Return rubric seeds from question bank/CSV, with fallback for demos."""
    question_rubrics = question_bank_to_rubrics(questions or [])
    if question_rubrics:
        return question_rubrics
    rubrics = load_rubrics_from_csv()
    if rubrics:
        return rubrics
    return _fallback_rubrics()


def build_seed_knowledge_documents() -> list[KnowledgeDocument]:
    """Return BNCC/Bloom/finance knowledge seed snippets for retrieval."""
    return load_knowledge_documents()


def _fallback_rubrics() -> list[Rubric]:
    """Return synthetic fallback rubrics when seed files have not been generated."""
    return [
        Rubric(
            rubric_id="rub_consumo_001",
            question_id="q_consumo_001",
            bncc_skill="BNCC-DEMO-MAT-FIN-001",
            bloom_level="analisar",
            financial_topic="consumo_consciente",
            criterion="Decidir entre gasto imediato e poupança com justificativa.",
            expected_concept="Priorizar necessidades, guardar parte do dinheiro e justificar consequência futura.",
            partial_concept="Menciona guardar dinheiro, mas sem explicar critério ou consequência.",
            misconception="Gastar tudo sem considerar necessidade, prioridade ou planejamento.",
        ),
        Rubric(
            rubric_id="rub_orcamento_001",
            question_id="q_orcamento_001",
            bncc_skill="BNCC-DEMO-MAT-FIN-002",
            bloom_level="aplicar",
            financial_topic="orcamento_pessoal",
            criterion="Organizar renda, despesas e reserva.",
            expected_concept="Separar despesas fixas, variáveis e reserva antes de compras não essenciais.",
            partial_concept="Lista gastos, mas não prioriza ou não separa reserva.",
            misconception="Tratar todo dinheiro disponível como dinheiro para consumo imediato.",
        ),
        Rubric(
            rubric_id="rub_juros_001",
            question_id="q_juros_001",
            bncc_skill="BNCC-DEMO-MAT-FIN-003",
            bloom_level="avaliar",
            financial_topic="juros_compostos",
            criterion="Explicar efeito do tempo sobre juros compostos.",
            expected_concept="Reconhecer que juros compostos crescem sobre montante acumulado ao longo do tempo.",
            partial_concept="Menciona juros, mas não explica composição ou tempo.",
            misconception="Confundir juros compostos com soma fixa sem crescimento acumulado.",
        ),
    ]
