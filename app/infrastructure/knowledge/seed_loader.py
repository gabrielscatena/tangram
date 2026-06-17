from __future__ import annotations

import csv
from pathlib import Path

from app.domain.entities import KnowledgeDocument, Rubric


DEFAULT_SEED_DIR = Path("data/seed")


def load_rubrics_from_csv(path: Path | str = DEFAULT_SEED_DIR / "rubrics_bncc_bloom.csv") -> list[Rubric]:
    """Load rubric rows from a CSV seed file.

    Args:
        path: CSV path with fields matching the Rubric dataclass.

    Returns:
        Loaded rubrics. If the file does not exist, an empty list is returned.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        return []

    rubrics: list[Rubric] = []
    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rubrics.append(
                Rubric(
                    rubric_id=row["rubric_id"],
                    question_id=row["question_id"],
                    bncc_skill=row["bncc_skill"],
                    bloom_level=row["bloom_level"],
                    financial_topic=row["financial_topic"],
                    criterion=row["criterion"],
                    expected_concept=row["expected_concept"],
                    partial_concept=row["partial_concept"],
                    misconception=row["misconception"],
                    version=row.get("version", "v0.1") or "v0.1",
                )
            )
    return rubrics


def load_knowledge_documents(seed_dir: Path | str = DEFAULT_SEED_DIR) -> list[KnowledgeDocument]:
    """Load BNCC, Bloom and financial-literacy seed snippets for retrieval.

    The files are intentionally small and demonstrative. They are not a replacement
    for the official BNCC text or a validated pedagogical ontology.

    Args:
        seed_dir: Folder containing the seed CSV files.

    Returns:
        Knowledge documents ready to be indexed by the retriever/vector DB.
    """
    base = Path(seed_dir)
    documents: list[KnowledgeDocument] = []
    documents.extend(_load_bncc_documents(base / "bncc_financial_education_demo.csv"))
    documents.extend(_load_bloom_documents(base / "bloom_taxonomy.csv"))
    documents.extend(_load_financial_concepts(base / "financial_concepts.csv"))
    return documents


def _load_bncc_documents(path: Path) -> list[KnowledgeDocument]:
    if not path.exists():
        return []
    docs: list[KnowledgeDocument] = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = " ".join(
                [
                    row.get("stage", ""),
                    row.get("grade_range", ""),
                    row.get("area", ""),
                    row.get("topic", ""),
                    row.get("skill_text", ""),
                    row.get("keywords", ""),
                    row.get("notes", ""),
                ]
            ).strip()
            docs.append(
                KnowledgeDocument(
                    document_id=row["document_id"],
                    source_type="bncc_seed",
                    title=row.get("title", row["document_id"]),
                    text=text,
                    metadata={
                        "code": row.get("code", ""),
                        "stage": row.get("stage", ""),
                        "grade_range": row.get("grade_range", ""),
                        "area": row.get("area", ""),
                        "topic": row.get("topic", ""),
                    },
                    version=row.get("version", "v0.1") or "v0.1",
                )
            )
    return docs


def _load_bloom_documents(path: Path) -> list[KnowledgeDocument]:
    if not path.exists():
        return []
    docs: list[KnowledgeDocument] = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = " ".join(
                [
                    row.get("level", ""),
                    row.get("description", ""),
                    row.get("student_action_examples", ""),
                    row.get("feedback_implication", ""),
                    row.get("keywords", ""),
                ]
            ).strip()
            docs.append(
                KnowledgeDocument(
                    document_id=row["document_id"],
                    source_type="bloom_seed",
                    title=f"Bloom: {row.get('level', '')}",
                    text=text,
                    metadata={"level": row.get("level", ""), "order": row.get("order", "")},
                    version=row.get("version", "v0.1") or "v0.1",
                )
            )
    return docs


def _load_financial_concepts(path: Path) -> list[KnowledgeDocument]:
    if not path.exists():
        return []
    docs: list[KnowledgeDocument] = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = " ".join(
                [
                    row.get("concept", ""),
                    row.get("definition", ""),
                    row.get("common_misconceptions", ""),
                    row.get("feedback_hint", ""),
                    row.get("keywords", ""),
                ]
            ).strip()
            docs.append(
                KnowledgeDocument(
                    document_id=row["document_id"],
                    source_type="financial_concept",
                    title=row.get("concept", row["document_id"]),
                    text=text,
                    metadata={"concept": row.get("concept", "")},
                    version=row.get("version", "v0.1") or "v0.1",
                )
            )
    return docs
