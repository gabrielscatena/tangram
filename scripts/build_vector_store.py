from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import build_seed_knowledge_documents, build_seed_rubrics
from app.infrastructure.vector_store.simple_tfidf_vector_repository import SimpleTfidfVectorRepository


def main() -> None:
    """Build a lightweight vector-store manifest from BNCC/Bloom/rubric seeds.

    This mock does not persist a real Chroma/FAISS index by default. It validates
    that all source files are loadable and creates a manifest that explains exactly
    which documents would be indexed in a production-like vector database.
    """
    rubrics = build_seed_rubrics()
    knowledge_documents = build_seed_knowledge_documents()
    retriever = SimpleTfidfVectorRepository(rubrics, documents=knowledge_documents)

    sample_queries = [
        "guardar dinheiro e comprar só o necessário",
        "explicar juros compostos e crescimento ao longo do tempo",
        "comparar renda, patrimônio e dividendos",
    ]
    samples = {
        query: [
            {
                "context_id": item.context_id,
                "source_type": item.source_type,
                "similarity": item.similarity,
                "metadata": item.metadata,
            }
            for item in retriever.retrieve(query, top_k=3)
        ]
        for query in sample_queries
    }

    output = Path("data/vector_store")
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "backend": "SimpleTfidfVectorRepository",
        "production_replacement_options": ["ChromaDB", "FAISS", "pgvector", "Qdrant"],
        "source_files": [
            "data/seed/rubrics_bncc_bloom.csv",
            "data/seed/bncc_financial_education_demo.csv",
            "data/seed/bloom_taxonomy.csv",
            "data/seed/financial_concepts.csv",
        ],
        "counts": {
            "rubrics": len(rubrics),
            "knowledge_documents": len(knowledge_documents),
            "total_indexed_items": len(rubrics) + len(knowledge_documents),
        },
        "sample_retrieval": samples,
        "important_note": "Seed files are demonstrative and must be replaced/validated with official BNCC excerpts and approved pedagogical rubrics before real use.",
    }
    (output / "vector_index_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "README.txt").write_text(
        "Vector store mock initialized from BNCC/Bloom/rubric seed files. See vector_index_manifest.json.\n",
        encoding="utf-8",
    )
    print("Vector store manifest built from BNCC/Bloom/rubric seed files.")


if __name__ == "__main__":
    main()
