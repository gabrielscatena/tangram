from app.bootstrap import build_seed_rubrics
from app.domain.entities import StudentResponse
from app.infrastructure.ml.feedback_generator import TemplateFeedbackGenerator
from app.infrastructure.ml.rule_based_classifier_service import RuleBasedClassifierService
from app.infrastructure.vector_store.simple_tfidf_vector_repository import SimpleTfidfVectorRepository


def test_feedback_generator_returns_formative_feedback() -> None:
    response = StudentResponse(
        response_id="r1",
        pseudo_student_id="s1",
        question_id="q_consumo_001",
        raw_text="Eu guardaria uma parte para o futuro e compraria só o necessário.",
        clean_text="Eu guardaria uma parte para o futuro e compraria só o necessário.",
        grade_level="7_ano",
    )
    context = SimpleTfidfVectorRepository(build_seed_rubrics()).retrieve(response.clean_text)
    classification = RuleBasedClassifierService().classify(response, context)
    feedback = TemplateFeedbackGenerator().generate(response, classification, context)
    assert feedback.feedback_text
    assert "resposta" in feedback.feedback_text.lower() or "revisar" in feedback.feedback_text.lower()
    assert feedback.template_id.startswith("tpl_")
