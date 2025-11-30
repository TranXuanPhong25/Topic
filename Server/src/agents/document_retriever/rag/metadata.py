"""Helpers for inspecting document metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

from langchain_community.document_loaders import PyPDFLoader

from .Load import DEFAULT_DATA_DIR


def extract_pdf_metadata(pdf_path: str | Path) -> Dict[str, str]:
    """
    Return the metadata of the first page of the provided PDF.
    """
    path = Path(pdf_path)
    loader = PyPDFLoader(str(path))
    docs = loader.load()
    if not docs:
        raise ValueError(f"Unable to load PDF: {path}")
    return docs[0].metadata or {}


def iter_metadata(
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> Iterable[tuple[str, Dict[str, str]]]:
    """
    Yield (filename, metadata) pairs for the PDFs inside the data directory.
    """
    data_path = Path(data_dir)
    for pdf_path in sorted(data_path.glob("*.pdf")):
        yield pdf_path.name, extract_pdf_metadata(pdf_path)


__all__ = ["extract_pdf_metadata", "iter_metadata"]
