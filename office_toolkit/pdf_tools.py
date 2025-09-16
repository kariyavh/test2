"""Helpers for merging PDF files."""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Iterable, List

from PyPDF2 import PdfMerger, PdfReader


@dataclass
class PdfMergeResult:
    """Outcome of merging user supplied PDFs."""

    data: BytesIO | None
    page_count: int
    errors: List[str]


def merge_pdfs(files: Iterable) -> PdfMergeResult:
    """Merge PDF files into a single PDF held in memory."""
    merger = PdfMerger()
    errors: List[str] = []
    total_pages = 0

    for uploaded in files:
        try:
            uploaded.seek(0)
        except Exception:
            pass
        try:
            reader = PdfReader(uploaded)
            total_pages += len(reader.pages)
            uploaded.seek(0)
            merger.append(reader)
        except Exception as exc:  # pragma: no cover - streamlit environment
            errors.append(f"Failed to merge {uploaded.name}: {exc}")

    output = BytesIO()
    if total_pages == 0:
        merger.close()
        return PdfMergeResult(data=None, page_count=0, errors=errors)

    merger.write(output)
    merger.close()
    output.seek(0)
    return PdfMergeResult(data=output, page_count=total_pages, errors=errors)
