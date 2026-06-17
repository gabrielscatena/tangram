from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PdfPageText:
    """Text extracted from one PDF page.

    Args:
        source_id: Stable identifier derived from the PDF path stem.
        source_path: Relative or absolute source PDF path.
        source_sha256: SHA256 hash of the PDF file.
        page_number: One-based page number.
        text: Extracted and normalized page text.
    """

    source_id: str
    source_path: str
    source_sha256: str
    page_number: int
    text: str


@dataclass(frozen=True)
class SourceChunk:
    """Versioned text chunk produced from an original source page.

    Args:
        chunk_id: Stable SHA256-derived chunk identifier.
        source_id: Stable identifier of the source document.
        source_path: Relative or absolute path of the source document.
        source_sha256: SHA256 hash of the source PDF file.
        page_number: One-based page number from which the chunk was extracted.
        chunk_index: Zero-based chunk index within the page.
        text: Chunk text.
        chunking_version: Identifier for the chunking algorithm/configuration.
        metadata: Additional source metadata.
    """

    chunk_id: str
    source_id: str
    source_path: str
    source_sha256: str
    page_number: int
    chunk_index: int
    text: str
    chunking_version: str
    metadata: dict[str, str]


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    """Calculate SHA256 for a file.

    Args:
        path: File path.
        block_size: Read block size in bytes.

    Returns:
        Hexadecimal SHA256 digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    """Calculate SHA256 for UTF-8 text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    """Normalize extracted PDF text for chunking.

    This function intentionally avoids aggressive cleanup because the raw wording
    of BNCC/MEC documents should remain auditable.

    Args:
        text: Raw extracted text.

    Returns:
        Normalized text with collapsed whitespace.
    """
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def make_source_id(pdf_path: Path, root_dir: Path) -> str:
    """Create a stable source ID from a PDF path relative to the raw root."""
    try:
        relative = pdf_path.relative_to(root_dir)
    except ValueError:
        relative = pdf_path.name
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", str(relative)).strip("_").lower()
    return safe.replace("_pdf", "")


def extract_pdf_pages(pdf_path: Path, root_dir: Path | None = None) -> list[PdfPageText]:
    """Extract normalized text page by page from a PDF.

    PyMuPDF is used when available because it is substantially faster for the
    official MEC/BCB PDFs. The function falls back to pypdf for portability.

    Args:
        pdf_path: PDF file to extract.
        root_dir: Optional root used to build stable source identifiers.

    Returns:
        List of PdfPageText records, one per page with non-empty text.

    Raises:
        RuntimeError: If no supported PDF extraction backend is installed.
    """
    root = root_dir or pdf_path.parent
    source_sha = sha256_file(pdf_path)
    source_id = make_source_id(pdf_path, root)

    raw_pages: list[tuple[int, str]] = []
    try:
        import fitz  # PyMuPDF

        document = fitz.open(str(pdf_path))
        raw_pages = [(idx, page.get_text("text") or "") for idx, page in enumerate(document, start=1)]
        document.close()
    except ImportError:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - environment-specific
            raise RuntimeError("PyMuPDF or pypdf is required. Install with: pip install pymupdf pypdf") from exc
        reader = PdfReader(str(pdf_path))
        raw_pages = [(idx, page.extract_text() or "") for idx, page in enumerate(reader.pages, start=1)]

    pages: list[PdfPageText] = []
    for idx, raw_text in raw_pages:
        text = normalize_text(raw_text)
        if not text:
            logger.warning("empty_pdf_page_text", extra={"pdf_path": str(pdf_path), "page_number": idx})
            continue
        pages.append(
            PdfPageText(
                source_id=source_id,
                source_path=str(pdf_path),
                source_sha256=source_sha,
                page_number=idx,
                text=text,
            )
        )
    return pages


def split_text_with_overlap(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into character-based chunks with overlap.

    Args:
        text: Text to split.
        chunk_size: Maximum chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks in characters.

    Returns:
        List of chunks.

    Raises:
        ValueError: If chunk configuration is invalid.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    clean_text = normalize_text(text)
    if not clean_text:
        return []
    if len(clean_text) <= chunk_size:
        return [clean_text]

    chunks: list[str] = []
    start = 0
    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        candidate = clean_text[start:end]
        if end < len(clean_text):
            # Prefer breaking at sentence/paragraph/space boundaries when close.
            boundary_candidates = [candidate.rfind("\n\n"), candidate.rfind(". "), candidate.rfind("; "), candidate.rfind(" ")]
            boundary = max(boundary_candidates)
            if boundary > int(chunk_size * 0.65):
                end = start + boundary + 1
                candidate = clean_text[start:end]
        chunks.append(candidate.strip())
        if end >= len(clean_text):
            break
        start = max(end - chunk_overlap, 0)
    return [chunk for chunk in chunks if chunk]


def page_to_chunks(
    page: PdfPageText,
    chunk_size: int,
    chunk_overlap: int,
    chunking_version: str,
) -> list[SourceChunk]:
    """Convert one extracted page into versioned chunks."""
    raw_chunks = split_text_with_overlap(page.text, chunk_size, chunk_overlap)
    chunks: list[SourceChunk] = []
    for index, chunk_text in enumerate(raw_chunks):
        basis = "|".join(
            [
                page.source_sha256,
                page.source_id,
                str(page.page_number),
                str(index),
                chunking_version,
                sha256_text(chunk_text),
            ]
        )
        chunk_id = f"chk_{sha256_text(basis)[:20]}"
        chunks.append(
            SourceChunk(
                chunk_id=chunk_id,
                source_id=page.source_id,
                source_path=page.source_path,
                source_sha256=page.source_sha256,
                page_number=page.page_number,
                chunk_index=index,
                text=chunk_text,
                chunking_version=chunking_version,
                metadata={
                    "text_sha256": sha256_text(chunk_text),
                    "char_count": str(len(chunk_text)),
                },
            )
        )
    return chunks


def write_jsonl(path: Path, records: Iterable[object]) -> None:
    """Write dataclass/dict records as JSON Lines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            payload = asdict(record) if hasattr(record, "__dataclass_fields__") else record
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_chunks_jsonl(path: Path) -> list[SourceChunk]:
    """Read SourceChunk records from JSON Lines."""
    chunks: list[SourceChunk] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            data = json.loads(line)
            chunks.append(SourceChunk(**data))
    return chunks


def build_chunks_from_raw_pdfs(
    raw_dir: Path,
    processed_dir: Path,
    chunk_size: int,
    chunk_overlap: int,
    chunking_version: str,
) -> list[SourceChunk]:
    """Run extraction and chunking over every PDF under raw_dir.

    Args:
        raw_dir: Directory containing original PDFs, recursively.
        processed_dir: Directory where page/chunk JSONL files will be written.
        chunk_size: Maximum chunk size in characters.
        chunk_overlap: Chunk overlap in characters.
        chunking_version: Version string included in every chunk.

    Returns:
        List of generated chunks.
    """
    pdf_paths = sorted(raw_dir.rglob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found under {raw_dir}")

    all_pages: list[PdfPageText] = []
    all_chunks: list[SourceChunk] = []
    for pdf_path in pdf_paths:
        logger.info("extracting_pdf", extra={"pdf_path": str(pdf_path)})
        pages = extract_pdf_pages(pdf_path, root_dir=raw_dir)
        all_pages.extend(pages)
        for page in pages:
            all_chunks.extend(page_to_chunks(page, chunk_size, chunk_overlap, chunking_version))

    write_jsonl(processed_dir / "source_pages.jsonl", all_pages)
    write_jsonl(processed_dir / "source_chunks.jsonl", all_chunks)
    return all_chunks


def source_file_records(raw_dir: Path) -> list[dict[str, object]]:
    """Build hash/size records for every original PDF file."""
    records: list[dict[str, object]] = []
    for pdf_path in sorted(raw_dir.rglob("*.pdf")):
        records.append(
            {
                "path": str(pdf_path),
                "relative_path": str(pdf_path.relative_to(raw_dir)),
                "sha256": sha256_file(pdf_path),
                "size_bytes": pdf_path.stat().st_size,
            }
        )
    return records


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    """Write a JSON manifest with indentation and UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
