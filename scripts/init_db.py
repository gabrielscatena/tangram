from __future__ import annotations

from pathlib import Path

DB_PATH = "data/duckdb/tangram_lab.duckdb"

SCHEMA = """
CREATE TABLE IF NOT EXISTS student_response (
    response_id VARCHAR PRIMARY KEY,
    pseudo_student_id VARCHAR,
    question_id VARCHAR,
    raw_text VARCHAR,
    clean_text VARCHAR,
    grade_level VARCHAR,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rubric (
    rubric_id VARCHAR PRIMARY KEY,
    question_id VARCHAR,
    bncc_skill VARCHAR,
    bloom_level VARCHAR,
    financial_topic VARCHAR,
    criterion VARCHAR,
    expected_concept VARCHAR,
    partial_concept VARCHAR,
    misconception VARCHAR,
    version VARCHAR
);

CREATE TABLE IF NOT EXISTS pending_review (
    response_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS human_review (
    review_id VARCHAR PRIMARY KEY,
    response_id VARCHAR,
    reviewer_role VARCHAR,
    corrected_label VARCHAR,
    edited_feedback VARCHAR,
    decision VARCHAR,
    created_at TIMESTAMP
);
"""


def main() -> None:
    """Initialize DuckDB schema when duckdb is available."""
    try:
        import duckdb
    except ImportError as exc:
        raise SystemExit("duckdb is not installed. Create the Conda environment first.") from exc
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(DB_PATH) as conn:
        conn.execute(SCHEMA)
    print(f"Initialized {DB_PATH}")


if __name__ == "__main__":
    main()
