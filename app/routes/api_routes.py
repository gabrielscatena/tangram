from __future__ import annotations

from app.domain.value_objects import EvaluationRequest
from app.infrastructure.knowledge.question_bank_loader import get_question_by_id
from app.routes._helpers import get_container

try:
    from flask import Blueprint, jsonify, request
except ImportError:  # pragma: no cover
    Blueprint = None  # type: ignore[assignment]

if Blueprint is not None:
    api_bp = Blueprint("api", __name__)

    @api_bp.route("/questions", methods=["GET"])
    def list_questions():
        """Return the loaded question bank."""
        container = get_container()
        return jsonify(
            [
                {
                    "question_id": q.question_id,
                    "title": q.title,
                    "prompt": q.prompt,
                    "grade_level": q.grade_level,
                    "financial_topic": q.financial_topic,
                    "bncc_area": q.bncc_area,
                    "bncc_skill": q.bncc_skill,
                    "bloom_level": q.bloom_level,
                    "difficulty": q.difficulty,
                    "expected_answer": q.expected_answer,
                }
                for q in container.questions
            ]
        )

    @api_bp.route("/evaluate", methods=["POST"])
    def evaluate_response():
        """Evaluate a response and return JSON."""
        payload = request.get_json(force=True)
        container = get_container()
        question_id = payload.get("question_id", "q001")
        question = get_question_by_id(container.questions, question_id)
        result = container.evaluate_response.execute(
            EvaluationRequest(
                student_id=payload.get("student_id", "demo-student"),
                question_id=question.question_id if question else question_id,
                raw_text=payload.get("student_response", payload.get("raw_text", "")),
                grade_level=(question.grade_level if question else payload.get("grade_level", "7_ano")),
                question_title=(question.title if question else payload.get("question_title", "")),
                question_prompt=(question.prompt if question else payload.get("question_prompt", "")),
                financial_topic=(question.financial_topic if question else payload.get("financial_topic", "")),
                bncc_skill=(question.bncc_skill if question else payload.get("bncc_skill", "")),
                bloom_level=(question.bloom_level if question else payload.get("bloom_level", "")),
                difficulty=(question.difficulty if question else payload.get("difficulty", "")),
                expected_answer=(question.expected_answer if question else payload.get("expected_answer", "")),
            )
        )
        return jsonify(
            {
                "response_id": result.response.response_id,
                "trace_id": result.trace_id,
                "question_id": result.response.question_id,
                "question_title": result.response.question_title,
                "conceptual_label": result.classification.conceptual_label.value,
                "confidence_score": result.classification.confidence_score,
                "ambiguity_score": result.ambiguity.ambiguity_score,
                "human_review_required": result.ambiguity.human_review_required,
                "feedback": result.feedback.feedback_text,
                "vector_backend": container.vector_backend,
                "retrieved_context": [
                    {
                        "context_id": item.context_id,
                        "source_type": item.source_type,
                        "similarity": item.similarity,
                        "metadata": item.metadata,
                        "preview": item.text[:300],
                    }
                    for item in result.retrieved_context
                ],
            }
        )
else:  # pragma: no cover
    api_bp = None
from pathlib import Path
import json

import joblib
from flask import current_app, jsonify, request
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity


_RAW_VECTOR_CACHE = {}


def _project_root() -> Path:
    """Return project root from Flask app folder."""
    return Path(current_app.root_path).parent


def _load_raw_vector_store() -> dict:
    """Load local TF-IDF vector store artifacts."""
    cache_key = "raw_pdf_tfidf"

    if cache_key in _RAW_VECTOR_CACHE:
        return _RAW_VECTOR_CACHE[cache_key]

    root = _project_root()
    vector_dir = root / "data" / "vector_store"

    vectorizer_path = vector_dir / "tfidf_vectorizer.joblib"
    matrix_path = vector_dir / "tfidf_matrix.npz"
    chunks_path = vector_dir / "indexed_chunks.jsonl"
    manifest_path = vector_dir / "vector_index_manifest.json"

    missing = [
        str(path)
        for path in [vectorizer_path, matrix_path, chunks_path, manifest_path]
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Raw vector store artifacts not found. "
            f"Missing: {missing}. "
            "Run scripts/build_raw_pdf_vector_db.py first."
        )

    vectorizer = joblib.load(vectorizer_path)
    matrix = load_npz(matrix_path)

    chunks = []
    with chunks_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    with manifest_path.open("r", encoding="utf-8") as file:
        manifest = json.load(file)

    store = {
        "backend": "raw_pdf_tfidf_vector_store",
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": chunks,
        "manifest": manifest,
    }

    _RAW_VECTOR_CACHE[cache_key] = store
    return store


def _search_raw_vector_store(query: str, top_k: int = 5) -> list[dict]:
    """Search local raw PDF vector store."""
    store = _load_raw_vector_store()

    query_vector = store["vectorizer"].transform([query])
    scores = cosine_similarity(query_vector, store["matrix"]).ravel()

    top_indexes = scores.argsort()[::-1][:top_k]

    results = []
    for rank, index in enumerate(top_indexes, start=1):
        chunk = store["chunks"][int(index)]

        results.append(
            {
                "rank": rank,
                "score": round(float(scores[int(index)]), 4),
                "chunk_id": chunk.get("chunk_id"),
                "source_id": chunk.get("source_id"),
                "source_path": chunk.get("source_path"),
                "page_number": chunk.get("page_number"),
                "chunk_index": chunk.get("chunk_index"),
                "preview": chunk.get("text", "")[:700],
            }
        )

    return results


@api_bp.get("/vector-search")
def vector_search_get():
    """Search raw PDF vector DB using query params."""
    query = request.args.get("q") or request.args.get("query") or ""
    top_k = int(request.args.get("top_k", "5"))

    if not query.strip():
        return jsonify({"error": "Missing query parameter: q"}), 400

    try:
        results = _search_raw_vector_store(query=query, top_k=top_k)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(
        {
            "backend": "raw_pdf_tfidf_vector_store",
            "query": query,
            "top_k": top_k,
            "results": results,
        }
    )


@api_bp.post("/vector-search")
def vector_search_post():
    """Search raw PDF vector DB using JSON payload."""
    payload = request.get_json(silent=True) or {}

    query = payload.get("query") or payload.get("q") or ""
    top_k = int(payload.get("top_k", 5))

    if not query.strip():
        return jsonify({"error": "Missing JSON field: query"}), 400

    try:
        results = _search_raw_vector_store(query=query, top_k=top_k)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(
        {
            "backend": "raw_pdf_tfidf_vector_store",
            "query": query,
            "top_k": top_k,
            "results": results,
        }
    )