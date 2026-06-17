from __future__ import annotations

from pathlib import Path

from app.domain.entities import HumanReview, Rubric, StudentResponse


class DuckDBConnectionFactory:
    """Lazy DuckDB connection factory."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def connect(self):
        """Return a DuckDB connection.

        Raises:
            RuntimeError: If duckdb is not installed.
        """
        try:
            import duckdb
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("duckdb is required for DuckDB repositories.") from exc
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(self._db_path)


class DuckDBResponseRepository:
    """DuckDB-backed response repository."""

    def __init__(self, connection_factory: DuckDBConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def save_response(self, response: StudentResponse) -> None:
        """Persist a response."""
        with self._connection_factory.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO student_response
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    response.response_id,
                    response.pseudo_student_id,
                    response.question_id,
                    response.raw_text,
                    response.clean_text,
                    response.grade_level,
                    response.created_at,
                ],
            )

    def get_response(self, response_id: str) -> StudentResponse | None:
        """Get a response."""
        with self._connection_factory.connect() as conn:
            row = conn.execute(
                "SELECT response_id, pseudo_student_id, question_id, raw_text, clean_text, grade_level, created_at FROM student_response WHERE response_id = ?",
                [response_id],
            ).fetchone()
        if row is None:
            return None
        return StudentResponse(*row)

    def list_pending_review(self) -> list[StudentResponse]:
        """List responses pending review."""
        with self._connection_factory.connect() as conn:
            rows = conn.execute(
                """
                SELECT sr.response_id, sr.pseudo_student_id, sr.question_id, sr.raw_text, sr.clean_text, sr.grade_level, sr.created_at
                FROM student_response sr
                INNER JOIN pending_review pr ON sr.response_id = pr.response_id
                """
            ).fetchall()
        return [StudentResponse(*row) for row in rows]

    def mark_pending_review(self, response_id: str) -> None:
        """Mark response as pending review."""
        with self._connection_factory.connect() as conn:
            conn.execute("INSERT OR REPLACE INTO pending_review VALUES (?)", [response_id])


class DuckDBRubricRepository:
    """DuckDB-backed rubric repository."""

    def __init__(self, connection_factory: DuckDBConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def list_rubrics(self) -> list[Rubric]:
        """Return all rubrics."""
        with self._connection_factory.connect() as conn:
            rows = conn.execute(
                """
                SELECT rubric_id, question_id, bncc_skill, bloom_level, financial_topic, criterion,
                       expected_concept, partial_concept, misconception, version
                FROM rubric
                """
            ).fetchall()
        return [Rubric(*row) for row in rows]

    def get_by_question(self, question_id: str) -> list[Rubric]:
        """Return rubrics by question."""
        return [rubric for rubric in self.list_rubrics() if rubric.question_id == question_id]


class DuckDBHumanReviewRepository:
    """DuckDB-backed human review repository."""

    def __init__(self, connection_factory: DuckDBConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def save_review(self, review: HumanReview) -> None:
        """Persist a human review."""
        with self._connection_factory.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO human_review
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    review.review_id,
                    review.response_id,
                    review.reviewer_role,
                    review.corrected_label.value,
                    review.edited_feedback,
                    review.decision,
                    review.created_at,
                ],
            )
