from pathlib import Path

import pytest

from app.infrastructure.knowledge.raw_pdf_pipeline import (
    PdfPageText,
    make_source_id,
    page_to_chunks,
    split_text_with_overlap,
)


def test_split_text_with_overlap_keeps_text_and_splits() -> None:
    text = "A" * 80 + ". " + "B" * 80 + ". " + "C" * 80
    chunks = split_text_with_overlap(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 2
    assert all(chunk for chunk in chunks)
    assert all(len(chunk) <= 110 for chunk in chunks)


def test_split_text_rejects_invalid_config() -> None:
    with pytest.raises(ValueError):
        split_text_with_overlap("abc", chunk_size=10, chunk_overlap=10)


def test_page_to_chunks_generates_stable_ids() -> None:
    page = PdfPageText(
        source_id="bncc_demo",
        source_path="data/raw/bncc/demo.pdf",
        source_sha256="abc123",
        page_number=1,
        text="Educação financeira e consumo consciente. " * 20,
    )
    chunks_a = page_to_chunks(page, chunk_size=120, chunk_overlap=20, chunking_version="v1")
    chunks_b = page_to_chunks(page, chunk_size=120, chunk_overlap=20, chunking_version="v1")
    assert chunks_a
    assert [chunk.chunk_id for chunk in chunks_a] == [chunk.chunk_id for chunk in chunks_b]
    assert chunks_a[0].metadata["text_sha256"]


def test_make_source_id_is_relative_and_safe() -> None:
    root = Path("/tmp/data/raw")
    pdf = root / "mec tct" / "Caderno Economia.pdf"
    assert make_source_id(pdf, root) == "mec_tct_caderno_economia"
