from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.infrastructure.knowledge.raw_pdf_pipeline import (
    build_chunks_from_raw_pdfs,
    read_chunks_jsonl,
    sha256_file,
    source_file_records,
    utc_now_iso,
    write_manifest,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the raw PDF vector database pipeline."""
    parser = argparse.ArgumentParser(
        description="Extract original PDFs, create versioned chunks, and build a local vector index."
    )
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--vector-dir", type=Path, default=Path("data/vector_store"))
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    parser.add_argument("--pipeline-version", default="raw_pdf_tfidf_v1.0")
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Reuse data/processed/source_chunks.jsonl instead of extracting PDFs again.",
    )
    return parser.parse_args()


def build_tfidf_index(chunks_path: Path, vector_dir: Path) -> dict[str, object]:
    """Fit and persist a TF-IDF vector index over source chunks.

    This is a lightweight local vector store for the mock. It is not a production
    replacement for Chroma, FAISS, Qdrant, pgvector, or managed vector search.
    """
    try:
        import joblib
        from scipy import sparse
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("scikit-learn, scipy and joblib are required for the TF-IDF vector index") from exc

    chunks = read_chunks_jsonl(chunks_path)
    texts = [chunk.text for chunk in chunks]
    if not texts:
        raise ValueError("No chunks available to index")

    vector_dir.mkdir(parents=True, exist_ok=True)
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        max_features=50000,
        min_df=1,
    )
    matrix = vectorizer.fit_transform(texts)

    vectorizer_path = vector_dir / "tfidf_vectorizer.joblib"
    matrix_path = vector_dir / "tfidf_matrix.npz"
    chunks_copy_path = vector_dir / "indexed_chunks.jsonl"

    joblib.dump(vectorizer, vectorizer_path)
    sparse.save_npz(matrix_path, matrix)
    chunks_copy_path.write_text(chunks_path.read_text(encoding="utf-8"), encoding="utf-8")

    return {
        "backend": "tfidf_local_vector_store",
        "vectorizer_path": str(vectorizer_path),
        "matrix_path": str(matrix_path),
        "indexed_chunks_path": str(chunks_copy_path),
        "indexed_chunks": len(chunks),
        "matrix_shape": list(matrix.shape),
        "artifact_hashes": {
            "vectorizer_sha256": sha256_file(vectorizer_path),
            "matrix_sha256": sha256_file(matrix_path),
            "indexed_chunks_sha256": sha256_file(chunks_copy_path),
        },
    }


def main() -> None:
    """Run the raw PDF knowledge-base pipeline."""
    args = parse_args()
    args.processed_dir.mkdir(parents=True, exist_ok=True)
    args.vector_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = args.processed_dir / "source_chunks.jsonl"
    if args.skip_extraction:
        if not chunks_path.exists():
            raise FileNotFoundError(f"Cannot skip extraction: {chunks_path} does not exist")
        logger.info("reusing_existing_chunks", extra={"chunks_path": str(chunks_path)})
    else:
        chunks = build_chunks_from_raw_pdfs(
            raw_dir=args.raw_dir,
            processed_dir=args.processed_dir,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            chunking_version=args.pipeline_version,
        )
        logger.info("chunks_created", extra={"count": len(chunks), "chunks_path": str(chunks_path)})

    index_info = build_tfidf_index(chunks_path, args.vector_dir)
    chunks = read_chunks_jsonl(chunks_path)
    source_records = source_file_records(args.raw_dir)

    processed_pages = args.processed_dir / "source_pages.jsonl"
    manifest = {
        "generated_at": utc_now_iso(),
        "pipeline_version": args.pipeline_version,
        "pipeline_steps": [
            "data/raw/**/*.pdf",
            "pdf_text_extraction_by_page_with_pypdf",
            "versioned_character_chunking_with_overlap",
            "data/processed/source_chunks.jsonl",
            "tfidf_embeddings",
            "local_vector_store_artifacts",
            "vector_index_manifest.json",
        ],
        "raw_dir": str(args.raw_dir),
        "processed_dir": str(args.processed_dir),
        "vector_dir": str(args.vector_dir),
        "chunking": {
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
        },
        "source_files": source_records,
        "counts": {
            "source_files": len(source_records),
            "chunks": len(chunks),
        },
        "processed_outputs": {
            "source_pages_path": str(processed_pages),
            "source_chunks_path": str(chunks_path),
            "source_pages_sha256": sha256_file(processed_pages) if processed_pages.exists() else None,
            "source_chunks_sha256": sha256_file(chunks_path),
        },
        "vector_index": index_info,
        "notes": [
            "This mock uses a local TF-IDF vector store for reproducibility and CPU-only execution.",
            "For production, replace this backend with Chroma, FAISS, pgvector, Qdrant, OpenSearch, or a managed vector database.",
            "Source PDFs remain auditable through SHA256 hashes and relative paths.",
        ],
    }
    write_manifest(args.vector_dir / "vector_index_manifest.json", manifest)
    print(json.dumps({"status": "ok", "chunks": len(chunks), "manifest": str(args.vector_dir / "vector_index_manifest.json")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
