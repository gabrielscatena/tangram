from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.bootstrap import build_demo_container
from app.domain.value_objects import EvaluationRequest


def main() -> None:
    """Run a full demo pipeline without Flask."""
    container = build_demo_container()
    result = container.evaluate_response.execute(
        EvaluationRequest(
            student_id="aluno-demo-001",
            question_id="q_consumo_001",
            raw_text="Eu guardaria uma parte porque posso precisar depois e compraria só o necessário.",
            grade_level="7_ano",
        )
    )
    print("=== Tangram AI Feedback Lab Demo ===")
    print(f"Response ID: {result.response.response_id}")
    print(f"Trace ID: {result.trace_id}")
    print(f"Label: {result.classification.conceptual_label.value}")
    print(f"Confidence: {result.classification.confidence_score}")
    print(f"Ambiguity: {result.ambiguity.ambiguity_score}")
    print(f"Human review required: {result.ambiguity.human_review_required}")
    print(f"Feedback: {result.feedback.feedback_text}")


if __name__ == "__main__":
    main()
