from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.infrastructure.knowledge.raw_pdf_pipeline import read_chunks_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local TF-IDF vector index built from original PDFs.")
    parser.add_argument("query", help="Natural-language search query")
    parser.add_argument("--vector-dir", type=Path, default=Path("data/vector_store"))
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        import joblib
        from scipy import sparse
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("scikit-learn, scipy and joblib are required") from exc

    vectorizer = joblib.load(args.vector_dir / "tfidf_vectorizer.joblib")
    matrix = sparse.load_npz(args.vector_dir / "tfidf_matrix.npz")
    chunks = read_chunks_jsonl(args.vector_dir / "indexed_chunks.jsonl")

    query_vector = vectorizer.transform([args.query])
    scores = cosine_similarity(query_vector, matrix).flatten()
    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[: args.top_k]
    results = []
    for idx, score in ranked:
        chunk = chunks[idx]
        results.append(
            {
                "score": round(float(score), 4),
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "source_path": chunk.source_path,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "preview": chunk.text[:500],
            }
        )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
