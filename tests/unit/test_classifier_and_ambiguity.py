from app.bootstrap import build_seed_rubrics
from app.domain.entities import StudentResponse
from app.infrastructure.ml.ambiguity_service import EntropyAmbiguityScorer
from app.infrastructure.ml.rule_based_classifier_service import RuleBasedClassifierService
from app.infrastructure.vector_store.simple_tfidf_vector_repository import SimpleTfidfVectorRepository


def test_classifier_marks_developed_financial_answer_as_correct_or_partial() -> None:
    response = StudentResponse(
        response_id="r1",
        pseudo_student_id="s1",
        question_id="q_consumo_001",
        raw_text="Eu guardaria uma parte para o futuro e compraria só o necessário.",
        clean_text="Eu guardaria uma parte para o futuro e compraria só o necessário.",
        grade_level="7_ano",
    )
    context = SimpleTfidfVectorRepository(build_seed_rubrics()).retrieve(response.clean_text)
    result = RuleBasedClassifierService().classify(response, context)
    assert result.conceptual_label.value in {"correct", "partially_correct"}
    assert result.confidence_score >= 0.6


def test_ambiguity_scorer_routes_short_vague_response_to_human_review() -> None:
    response = StudentResponse(
        response_id="r1",
        pseudo_student_id="s1",
        question_id="q_consumo_001",
        raw_text="Não sei.",
        clean_text="Não sei.",
        grade_level="7_ano",
    )
    context = SimpleTfidfVectorRepository(build_seed_rubrics()).retrieve(response.clean_text)
    classification = RuleBasedClassifierService().classify(response, context)
    ambiguity = EntropyAmbiguityScorer(review_threshold=0.58).score(response, classification, context)
    assert ambiguity.human_review_required is True
    assert ambiguity.ambiguity_score >= 0.58 or classification.confidence_score < 0.60
