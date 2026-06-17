from app.bootstrap import build_demo_container
from app.domain.value_objects import EvaluationRequest, ReviewRequest


def test_annotation_use_case_saves_human_review() -> None:
    container = build_demo_container()
    result = container.evaluate_response.execute(
        EvaluationRequest(student_id="student-1", question_id="q_consumo_001", raw_text="Não sei.")
    )
    review = container.annotate_response.execute(
        ReviewRequest(
            response_id=result.response.response_id,
            reviewer_role="pedagogia",
            corrected_label="vague",
            edited_feedback="Explique melhor sua decisão e dê um exemplo.",
            decision="approved",
        )
    )
    assert review.review_id.startswith("review_")
    assert review.response_id == result.response.response_id
