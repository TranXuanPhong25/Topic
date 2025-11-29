"""Embedding helpers for building the RAG vector store."""

from __future__ import annotations

import logging
import os
from typing import Iterable, Sequence

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

LOGGER = logging.getLogger(__name__)
DEFAULT_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-on-pinecone")
DEFAULT_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "models/text-embedding-004")
DEFAULT_PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
DEFAULT_PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")


def create_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> GoogleGenerativeAIEmbeddings:
    """Instantiate the Google embedding model used across the RAG stack."""
    LOGGER.info("Using embedding model: %s", model_name)
    return GoogleGenerativeAIEmbeddings(model=model_name)


def ensure_pinecone_index(
    *,
    index_name: str = DEFAULT_INDEX_NAME,
    dimension: int = 768,
    api_key: str | None = None,
    cloud: str = DEFAULT_PINECONE_CLOUD,
    region: str = DEFAULT_PINECONE_REGION,
) -> Pinecone:
    """
    Ensure the Pinecone index exists and return the client instance.
    """
    api_key = api_key or os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PINECONE_API_KEY environment variable.")

    pc = Pinecone(api_key=api_key)
    existing_indexes = pc.list_indexes().names()
    if index_name not in existing_indexes:
        LOGGER.info("Creating Pinecone index '%s' (dimension=%s)", index_name, dimension)
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
    else:
        LOGGER.debug("Pinecone index '%s' already exists", index_name)
    return pc


def index_documents(
    documents: Sequence[Document],
    *,
    index_name: str = DEFAULT_INDEX_NAME,
    embedding_model: GoogleGenerativeAIEmbeddings | None = None,
    dimension: int = 768,
) -> PineconeVectorStore:
    """
    Create (if needed) and populate the Pinecone index with provided documents.
    """
    if not documents:
        raise ValueError("No documents provided for indexing.")

    embeddings = embedding_model or create_embedding_model()
    ensure_pinecone_index(index_name=index_name, dimension=dimension)
    LOGGER.info("Uploading %s documents to Pinecone index '%s'", len(documents), index_name)
    return PineconeVectorStore.from_documents(documents, embeddings, index_name=index_name)


def connect_vector_store(
    *,
    index_name: str = DEFAULT_INDEX_NAME,
    embedding_model: GoogleGenerativeAIEmbeddings | None = None,
) -> PineconeVectorStore:
    """
    Connect to an existing PineconeVectorStore instance.
    """
    embeddings = embedding_model or create_embedding_model()
    LOGGER.info("Connecting to Pinecone index '%s'", index_name)
    return PineconeVectorStore.from_existing_index(index_name, embeddings)


__all__ = [
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_INDEX_NAME",
    "DEFAULT_PINECONE_CLOUD",
    "DEFAULT_PINECONE_REGION",
    "connect_vector_store",
    "create_embedding_model",
    "ensure_pinecone_index",
    "index_documents",
]