from app.bootstrap import build_demo_container
from app.domain.value_objects import EvaluationRequest


def test_evaluate_response_full_pipeline_auto_feedback() -> None:
    container = build_demo_container()
    result = container.evaluate_response.execute(
        EvaluationRequest(
            student_id="student-1",
            question_id="q_consumo_001",
            raw_text="Eu guardaria uma parte para o futuro e compraria só o necessário.",
        )
    )
    assert result.response.response_id.startswith("resp_")
    assert result.trace_id.startswith("trc_")
    assert result.feedback.feedback_text
    assert len(result.retrieved_context) > 0
    assert len(container.trace_service.list_steps()) >= 4


def test_evaluate_response_full_pipeline_routes_vague_answer() -> None:
    container = build_demo_container()
    result = container.evaluate_response.execute(
        EvaluationRequest(
            student_id="student-1",
            question_id="q_consumo_001",
            raw_text="Não sei.",
        )
    )
    assert result.ambiguity.human_review_required is True
    pending = container.response_repository.list_pending_review()
    assert len(pending) == 1
    assert pending[0].response_id == result.response.response_id
