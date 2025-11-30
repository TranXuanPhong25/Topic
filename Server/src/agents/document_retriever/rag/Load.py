"""Document loading utilities for the RAG module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Sequence

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

LOGGER = logging.getLogger(__name__)
DEFAULT_DATA_DIR = Path(__file__).parent / "Data"
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def load_documents(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    *,
    encoding: str = "utf-8",
) -> List[Document]:
    """
    Load PDF/TXT documents from the provided directory.

    Returns a list of LangChain Document objects with basic metadata.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_path}")

    documents: List[Document] = []
    for path in sorted(data_path.iterdir()):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            loader = PyPDFLoader(str(path))
        elif suffix == ".txt":
            loader = TextLoader(str(path), encoding=encoding)
        else:
            LOGGER.debug("Skipping unsupported file: %s", path.name)
            continue

        loaded_docs = loader.load()
        for doc in loaded_docs:
            doc.metadata.setdefault("source", str(path))
            doc.metadata.setdefault("file_name", path.name)
        documents.extend(loaded_docs)

    LOGGER.info("Loaded %s documents from %s", len(documents), data_path)
    return documents


def clean_documents(documents: Iterable[Document]) -> List[Document]:
    """
    Normalize whitespace and remove control characters from documents.
    """
    cleaned: List[Document] = []
    for doc in documents:
        text = doc.page_content
        text = (
            text.replace("\n", " ")
            .replace("\t", " ")
            .replace("\xa0", " ")
            .replace("\x00", "")
            .replace("\r", " ")
        )
        doc.page_content = " ".join(text.split())
        cleaned.append(doc)
    return cleaned


def chunk_documents(
    documents: Sequence[Document],
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> List[Document]:
    """
    Split documents into smaller chunks for indexing/retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(list(documents))
    LOGGER.info("Created %s chunks (size=%s, overlap=%s)", len(chunks), chunk_size, chunk_overlap)
    return chunks


def load_and_chunk_documents(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> List[Document]:
    """
    Convenience helper that loads, cleans, and chunks documents in one call.
    """
    docs = load_documents(data_dir)
    docs = clean_documents(docs)
    return chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


__all__ = [
    "DEFAULT_DATA_DIR",
    "SUPPORTED_EXTENSIONS",
    "clean_documents",
    "chunk_documents",
    "load_and_chunk_documents",
    "load_documents",
]