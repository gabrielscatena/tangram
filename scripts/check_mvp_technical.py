"""Technical MVP checker for Tangram AI Feedback Lab.

This script validates whether the local demo app is using the question bank,
raw PDF vector DB, RAG retrieval, trace endpoints, and human-review flow.

Run with the Flask app already running:

    python scripts/check_mvp_technical.py --base-url http://127.0.0.1:5000

It performs both filesystem checks and HTTP API checks.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass
class CheckResult:
    """Single check result."""

    name: str
    passed: bool
    details: str
    critical: bool = True


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON dictionary.
    """
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def http_get_json(url: str, timeout: int = 10) -> dict[str, Any] | list[Any]:
    """Perform HTTP GET and parse JSON response.

    Args:
        url: Target URL.
        timeout: Timeout in seconds.

    Returns:
        Parsed JSON object.

    Raises:
        RuntimeError: If the request fails or response is not JSON.
    """
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except (HTTPError, URLError, ConnectionResetError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GET failed for {url}: {exc}") from exc


def http_get_text(url: str, timeout: int = 10) -> str:
    """Perform HTTP GET and return text.

    Args:
        url: Target URL.
        timeout: Timeout in seconds.

    Returns:
        Response body.
    """
    request = Request(url, headers={"Accept": "text/html"}, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"GET failed for {url}: {exc}") from exc


def http_post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    """Perform HTTP POST with JSON payload and parse JSON response.

    Args:
        url: Target URL.
        payload: JSON payload.
        timeout: Timeout in seconds.

    Returns:
        Parsed JSON dictionary.
    """
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except (HTTPError, URLError, ConnectionResetError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"POST failed for {url}: {exc}") from exc


def normalize_json_text(value: Any) -> str:
    """Convert arbitrary JSON-like object to lowercase searchable text.

    Args:
        value: Any object.

    Returns:
        Lowercase JSON string.
    """
    return json.dumps(value, ensure_ascii=False, default=str).lower()


def check_question_bank_file(project_root: Path) -> CheckResult:
    """Check local question bank CSV."""
    path = project_root / "data" / "seed" / "question_bank.csv"
    if not path.exists():
        return CheckResult("question_bank_file", False, f"Missing file: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    required_columns = {
        "question_id",
        "title",
        "prompt",
        "grade_level",
        "financial_topic",
        "bncc_skill",
        "bloom_level",
        "difficulty",
        "expected_answer",
    }
    columns = set(rows[0].keys()) if rows else set()
    missing_columns = sorted(required_columns - columns)

    difficulties = {row.get("difficulty", "") for row in rows}

    if len(rows) < 50:
        return CheckResult(
            "question_bank_file",
            False,
            f"Expected at least 50 questions, found {len(rows)}.",
        )

    if missing_columns:
        return CheckResult(
            "question_bank_file",
            False,
            f"Missing columns: {missing_columns}",
        )

    if not {"facil", "medio", "dificil"}.issubset(difficulties):
        return CheckResult(
            "question_bank_file",
            False,
            f"Missing expected difficulties. Found: {sorted(difficulties)}",
        )

    return CheckResult(
        "question_bank_file",
        True,
        f"OK: {len(rows)} questions, difficulties={sorted(difficulties)}",
    )


def check_vector_manifest(project_root: Path) -> CheckResult:
    """Check vector index manifest and artifacts."""
    manifest_path = project_root / "data" / "vector_store" / "vector_index_manifest.json"
    if not manifest_path.exists():
        return CheckResult(
            "vector_manifest",
            False,
            f"Missing file: {manifest_path}. Run build_raw_pdf_vector_db.py first.",
        )

    manifest = read_json(manifest_path)
    backend = manifest.get("vector_index", {}).get("backend")
    counts = manifest.get("counts", {})
    chunks = int(counts.get("chunks", 0))
    source_files = int(counts.get("source_files", 0))
    source_file_items = manifest.get("source_files", [])

    required_artifacts = [
        manifest.get("processed_outputs", {}).get("source_chunks_path"),
        manifest.get("vector_index", {}).get("vectorizer_path"),
        manifest.get("vector_index", {}).get("matrix_path"),
        manifest.get("vector_index", {}).get("indexed_chunks_path"),
    ]
    missing_artifacts = [
        str(project_root / artifact)
        for artifact in required_artifacts
        if artifact and not (project_root / artifact).exists()
    ]

    missing_sources = [
        item.get("path")
        for item in source_file_items
        if item.get("path") and not (project_root / item["path"]).exists()
    ]

    if backend != "tfidf_local_vector_store":
        return CheckResult(
            "vector_manifest",
            False,
            f"Unexpected backend={backend!r}. Expected tfidf_local_vector_store.",
        )

    if chunks <= 0 or source_files <= 0:
        return CheckResult(
            "vector_manifest",
            False,
            f"Invalid counts: chunks={chunks}, source_files={source_files}",
        )

    if missing_artifacts:
        return CheckResult(
            "vector_manifest",
            False,
            f"Missing vector artifacts: {missing_artifacts}",
        )

    if missing_sources:
        return CheckResult(
            "vector_manifest",
            False,
            f"Missing raw source PDFs: {missing_sources}",
        )

    return CheckResult(
        "vector_manifest",
        True,
        f"OK: backend={backend}, chunks={chunks}, source_files={source_files}",
    )


def check_student_page(base_url: str) -> CheckResult:
    """Check Student Playground page."""
    html = http_get_text(f"{base_url}/student")
    lower = html.lower()

    signals = [
        "q001",
        "q050",
        "consumo consciente",
        "ética em recomendações financeiras",
    ]
    missing = [signal for signal in signals if signal not in lower]

    if missing:
        return CheckResult(
            "student_page_question_dropdown",
            False,
            f"Student page loaded, but missing signals: {missing}",
        )

    return CheckResult(
        "student_page_question_dropdown",
        True,
        "OK: /student contains question bank signals q001..q050.",
    )


def check_questions_api(base_url: str) -> CheckResult:
    """Check /api/questions endpoint."""
    data = http_get_json(f"{base_url}/api/questions")

    if isinstance(data, dict):
        questions = data.get("questions") or data.get("data") or []
    elif isinstance(data, list):
        questions = data
    else:
        questions = []

    if len(questions) < 50:
        return CheckResult(
            "api_questions",
            False,
            f"Expected at least 50 questions from /api/questions, got {len(questions)}.",
        )

    ids = {item.get("question_id") for item in questions if isinstance(item, dict)}
    if "q001" not in ids or "q050" not in ids:
        return CheckResult(
            "api_questions",
            False,
            "Questions API did not include q001 and q050.",
        )

    return CheckResult("api_questions", True, f"OK: {len(questions)} questions returned.")


def check_vector_search_api(base_url: str) -> CheckResult:
    """Check /api/vector-search endpoint."""
    query = urlencode({"q": "educação financeira consumo consciente", "top_k": "5"})
    url = f"{base_url}/api/vector-search?{query}"

    try:
        data = http_get_json(url)
    except RuntimeError:
        payload = {
            "query": "educação financeira consumo consciente",
            "top_k": 5,
        }
        data = http_post_json(f"{base_url}/api/vector-search", payload)

    text = normalize_json_text(data)
    required_signals = ["source", "page", "chunk"]
    missing = [signal for signal in required_signals if signal not in text]

    if missing:
        return CheckResult(
            "api_vector_search",
            False,
            f"Vector search responded, but missing signals {missing}. Response preview: {text[:500]}",
        )

    if not any(signal in text for signal in ["mec_tct", "bncc", "bcb", ".pdf"]):
        return CheckResult(
            "api_vector_search",
            False,
            f"Vector search did not seem to return original PDF sources. Preview: {text[:500]}",
        )

    return CheckResult(
        "api_vector_search",
        True,
        "OK: vector search returned source/page/chunk signals from original documents.",
    )


def check_evaluate_and_trace(base_url: str, project_root: Path) -> list[CheckResult]:
    """Check evaluation endpoint and trace endpoint.

    Args:
        base_url: Flask base URL.
        project_root: Project root.

    Returns:
        List of check results.
    """
    results: list[CheckResult] = []

    payload = {
        "student_id": "mvp-checker",
        "question_id": "q017",
        "student_response": (
            "A dívida cresce porque os juros entram no valor devido "
            "e depois novos juros são calculados sobre esse total, gerando juros sobre juros."
        ),
    }

    data = http_post_json(f"{base_url}/api/evaluate", payload)
    text = normalize_json_text(data)

    trace_id = (
        data.get("trace_id")
        or data.get("trace", {}).get("trace_id")
        or data.get("result", {}).get("trace_id")
    )

    if not trace_id:
        results.append(
            CheckResult(
                "api_evaluate_trace_id",
                False,
                f"/api/evaluate did not return trace_id. Response preview: {text[:700]}",
            )
        )
        return results

    results.append(
        CheckResult(
            "api_evaluate_trace_id",
            True,
            f"OK: /api/evaluate returned trace_id={trace_id}",
        )
    )

    source_signals = ["source_path", "page_number", ".pdf", "retrieved"]
    if not any(signal in text for signal in source_signals):
        results.append(
            CheckResult(
                "api_evaluate_retrieved_sources",
                False,
                f"Evaluation response does not expose retrieved source evidence. Preview: {text[:700]}",
            )
        )
    else:
        results.append(
            CheckResult(
                "api_evaluate_retrieved_sources",
                True,
                "OK: evaluation response contains retrieved-source signals.",
            )
        )

    backend_ok = any(
        signal in text
        for signal in [
            "raw_pdf_tfidf_vector_store",
            "tfidf_local_vector_store",
            "raw_pdf_tfidf",
        ]
    )
    if not backend_ok:
        results.append(
            CheckResult(
                "api_evaluate_raw_backend",
                False,
                "Evaluation response does not clearly indicate raw PDF vector backend.",
                critical=False,
            )
        )
    else:
        results.append(
            CheckResult(
                "api_evaluate_raw_backend",
                True,
                "OK: evaluation response indicates raw/TF-IDF vector backend.",
            )
        )

    try:
        trace_data = http_get_json(f"{base_url}/api/traces/{trace_id}")
        trace_text = normalize_json_text(trace_data)
    except RuntimeError as exc:
        results.append(
            CheckResult(
                "api_trace_detail",
                False,
                f"Could not load /api/traces/{trace_id}: {exc}",
            )
        )
        trace_text = ""

    if trace_text:
        expected_trace_signals = [
            "question",
            "student",
            "retriev",
            "classif",
            "ambigu",
            "feedback",
        ]
        missing_trace_signals = [
            signal for signal in expected_trace_signals if signal not in trace_text
        ]

        if missing_trace_signals:
            results.append(
                CheckResult(
                    "api_trace_detail_content",
                    False,
                    f"Trace exists but misses signals: {missing_trace_signals}. Preview: {trace_text[:700]}",
                )
            )
        else:
            results.append(
                CheckResult(
                    "api_trace_detail_content",
                    True,
                    "OK: trace includes question/student/retrieval/classification/ambiguity/feedback signals.",
                )
            )

    trace_found_in_files = False
    for jsonl_path in (project_root / "data").rglob("*.jsonl"):
        try:
            if trace_id in jsonl_path.read_text(encoding="utf-8", errors="replace"):
                trace_found_in_files = True
                break
        except OSError:
            continue

    if trace_found_in_files:
        results.append(
            CheckResult(
                "trace_persistence",
                True,
                f"OK: trace_id={trace_id} found in local data/*.jsonl persistence.",
            )
        )
    else:
        results.append(
            CheckResult(
                "trace_persistence",
                False,
                f"trace_id={trace_id} not found in data/**/*.jsonl. Persistence may be API-only or not implemented.",
                critical=False,
            )
        )

    return results


def check_human_review_flow(base_url: str) -> list[CheckResult]:
    """Check whether ambiguous answers go to human review."""
    results: list[CheckResult] = []

    payload = {
        "student_id": "mvp-checker-ambiguous",
        "question_id": "q038",
        "student_response": "Não sei.",
    }

    try:
        data = http_post_json(f"{base_url}/api/evaluate", payload)
    except RuntimeError as exc:
        return [
            CheckResult(
                "human_review_trigger",
                False,
                f"Could not evaluate ambiguous response: {exc}",
            )
        ]

    text = normalize_json_text(data)
    review_signals = [
        "human_review_required",
        "review_required",
        "teacher_review",
        "revis",
    ]

    if not any(signal in text for signal in review_signals):
        results.append(
            CheckResult(
                "human_review_trigger",
                False,
                f"Ambiguous response did not expose human-review signal. Preview: {text[:700]}",
                critical=False,
            )
        )
    else:
        results.append(
            CheckResult(
                "human_review_trigger",
                True,
                "OK: ambiguous response exposes human-review signal.",
            )
        )

    try:
        teacher_html = http_get_text(f"{base_url}/teacher/review")
        teacher_text = teacher_html.lower()
    except RuntimeError as exc:
        results.append(
            CheckResult(
                "teacher_review_page",
                False,
                f"Could not load /teacher/review: {exc}",
                critical=False,
            )
        )
        return results

    if "não sei" in teacher_text or "mvp-checker-ambiguous" in teacher_text or "q038" in teacher_text:
        results.append(
            CheckResult(
                "teacher_review_queue_visibility",
                True,
                "OK: ambiguous response appears to be visible in Teacher Review page.",
            )
        )
    else:
        results.append(
            CheckResult(
                "teacher_review_queue_visibility",
                False,
                "Teacher Review page loads, but the ambiguous test response was not found.",
                critical=False,
            )
        )

    return results


def run_checks(project_root: Path, base_url: str) -> list[CheckResult]:
    """Run all MVP checks."""
    checks: list[CheckResult] = []

    checks.append(check_question_bank_file(project_root))
    checks.append(check_vector_manifest(project_root))

    try:
        checks.append(check_student_page(base_url))
    except RuntimeError as exc:
        checks.append(CheckResult("student_page_question_dropdown", False, str(exc)))

    try:
        checks.append(check_questions_api(base_url))
    except RuntimeError as exc:
        checks.append(CheckResult("api_questions", False, str(exc)))

    try:
        checks.append(check_vector_search_api(base_url))
    except RuntimeError as exc:
        checks.append(CheckResult("api_vector_search", False, str(exc)))

    try:
        checks.extend(check_evaluate_and_trace(base_url, project_root))
    except RuntimeError as exc:
        checks.append(CheckResult("api_evaluate_and_trace", False, str(exc)))

    checks.extend(check_human_review_flow(base_url))

    return checks


def print_report(results: list[CheckResult]) -> int:
    """Print check report.

    Args:
        results: List of check results.

    Returns:
        Process exit code.
    """
    print("\n=== Tangram AI Feedback Lab — Technical MVP Check ===\n")

    failed_critical = 0
    failed_noncritical = 0

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        severity = "critical" if result.critical else "non-critical"

        print(f"[{status}] {result.name} ({severity})")
        print(f"       {result.details}\n")

        if not result.passed and result.critical:
            failed_critical += 1
        elif not result.passed:
            failed_noncritical += 1

    passed = sum(result.passed for result in results)
    total = len(results)

    print("=== Summary ===")
    print(f"Passed: {passed}/{total}")
    print(f"Critical failures: {failed_critical}")
    print(f"Non-critical warnings: {failed_noncritical}")

    if failed_critical:
        print("\nRESULT: NOT READY for technical MVP.")
        return 1

    if failed_noncritical:
        print("\nRESULT: CLOSE to technical MVP, but fix warnings before demo.")
        return 0

    print("\nRESULT: READY for technical MVP demo.")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root. Default: current directory.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://127.0.0.1:5000",
        help="Running Flask app base URL.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the MVP checker."""
    args = parse_args()
    project_root = args.project_root.resolve()
    base_url = args.base_url.rstrip("/")

    results = run_checks(project_root=project_root, base_url=base_url)
    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())