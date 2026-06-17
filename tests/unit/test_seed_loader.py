from pathlib import Path

from app.infrastructure.knowledge.seed_loader import load_knowledge_documents, load_rubrics_from_csv


def test_seed_loader_loads_bncc_bloom_and_financial_documents() -> None:
    documents = load_knowledge_documents(Path("data/seed"))
    source_types = {document.source_type for document in documents}
    assert "bncc_seed" in source_types
    assert "bloom_seed" in source_types
    assert "financial_concept" in source_types


def test_seed_loader_loads_rubrics_from_csv() -> None:
    rubrics = load_rubrics_from_csv(Path("data/seed/rubrics_bncc_bloom.csv"))
    assert rubrics
    assert rubrics[0].bncc_skill.startswith("BNCC-DEMO")
