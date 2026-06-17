from __future__ import annotations

from app.domain.entities import Question
from app.domain.value_objects import EvaluationRequest
from app.infrastructure.knowledge.question_bank_loader import get_question_by_id
from app.routes._helpers import get_container

try:
    from flask import Blueprint, render_template, request
except ImportError:  # pragma: no cover
    Blueprint = None  # type: ignore[assignment]


def _fallback_question() -> Question:
    """Return one in-code question if the CSV is unavailable."""
    return Question(
        question_id="q001",
        title="Consumo consciente",
        prompt="Você recebeu R$ 50. Como decidiria entre gastar tudo hoje ou guardar parte?",
        grade_level="6_ano",
        financial_topic="consumo_consciente",
        bncc_area="Matemática",
        bncc_skill="BNCC_DEMO_EF_MAT_EDFIN_CONSUMO_01",
        bloom_level="compreender",
        difficulty="facil",
        expected_answer="Espera-se que o estudante mencione planejamento, necessidade, desejo e a possibilidade de guardar parte do dinheiro.",
        rubric_conceptual="Reconhece diferença entre necessidade e desejo.",
        rubric_clarity="Explica a decisão com linguagem simples.",
        rubric_structure="Apresenta decisão e justificativa.",
    )


if Blueprint is not None:
    student_bp = Blueprint("student", __name__)

    @student_bp.route("/", methods=["GET"])
    def index():
        """Render app homepage."""
        return render_template("index.html")

    @student_bp.route("/student", methods=["GET", "POST"])
    def student_playground():
        """Render student response demo with question-bank selection."""
        container = get_container()
        questions = container.questions or [_fallback_question()]
        result = None
        selected_question_id = request.form.get("question_id") or request.args.get("question_id") or questions[0].question_id
        selected_question = get_question_by_id(questions, selected_question_id) or questions[0]

        if request.method == "POST":
            result = container.evaluate_response.execute(
                EvaluationRequest(
                    student_id=request.form.get("student_id", "demo-student"),
                    question_id=selected_question.question_id,
                    raw_text=request.form.get("raw_text", ""),
                    grade_level=selected_question.grade_level,
                    question_title=selected_question.title,
                    question_prompt=selected_question.prompt,
                    financial_topic=selected_question.financial_topic,
                    bncc_skill=selected_question.bncc_skill,
                    bloom_level=selected_question.bloom_level,
                    difficulty=selected_question.difficulty,
                    expected_answer=selected_question.expected_answer,
                )
            )
        return render_template(
            "student_playground.html",
            result=result,
            questions=questions,
            selected_question=selected_question,
            vector_backend=container.vector_backend,
        )
else:  # pragma: no cover
    student_bp = None
