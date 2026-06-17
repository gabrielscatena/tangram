from __future__ import annotations

import csv
from pathlib import Path

from app.domain.entities import Question, Rubric

DEFAULT_QUESTION_BANK_PATH = Path("data/seed/question_bank.csv")


def load_question_bank(path: Path = DEFAULT_QUESTION_BANK_PATH) -> list[Question]:
    """Load the demo question bank from CSV.

    Args:
        path: CSV path containing question bank rows.

    Returns:
        List of questions. Returns an empty list if the file does not exist.
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            Question(
                question_id=row.get("question_id", "").strip(),
                title=row.get("title", "").strip(),
                prompt=row.get("prompt", "").strip(),
                grade_level=row.get("grade_level", "").strip(),
                financial_topic=row.get("financial_topic", "").strip(),
                bncc_area=row.get("bncc_area", "").strip(),
                bncc_skill=row.get("bncc_skill", "").strip(),
                bloom_level=row.get("bloom_level", "").strip(),
                difficulty=row.get("difficulty", "").strip(),
                expected_answer=row.get("expected_answer", "").strip(),
                rubric_conceptual=row.get("rubric_conceptual", "").strip(),
                rubric_clarity=row.get("rubric_clarity", "").strip(),
                rubric_structure=row.get("rubric_structure", "").strip(),
            )
            for row in reader
            if row.get("question_id")
        ]


def question_bank_to_rubrics(questions: list[Question]) -> list[Rubric]:
    """Convert question-bank rows to rubric objects.

    This makes every question available to the existing rubric/retrieval layer
    without requiring a separate authoring flow.

    Args:
        questions: Loaded question bank.

    Returns:
        Rubrics derived from question-bank metadata.
    """
    rubrics: list[Rubric] = []
    for question in questions:
        rubrics.append(
            Rubric(
                rubric_id=f"rub_{question.question_id}",
                question_id=question.question_id,
                bncc_skill=question.bncc_skill,
                bloom_level=question.bloom_level,
                financial_topic=question.financial_topic,
                criterion=" | ".join(
                    part
                    for part in [
                        question.title,
                        question.rubric_conceptual,
                        question.rubric_clarity,
                        question.rubric_structure,
                    ]
                    if part
                ),
                expected_concept=question.expected_answer,
                partial_concept=question.rubric_conceptual,
                misconception="Resposta vaga, sem justificativa ou desconectada do conceito financeiro esperado.",
                version="question_bank_v1",
            )
        )
    return rubrics


def get_question_by_id(questions: list[Question], question_id: str) -> Question | None:
    """Return a question by id from a loaded question list."""
    return next((question for question in questions if question.question_id == question_id), None)
