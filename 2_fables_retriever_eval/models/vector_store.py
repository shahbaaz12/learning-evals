"""Shared settings and a connection to the local Chroma collection."""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = f"classic_fables_{CHUNK_SIZE}_{CHUNK_OVERLAP}_cosine"


def load_vector_store(create=False):
    """Open the existing collection; allow creation only during indexing."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(PROJECT_ROOT / "chroma_store"),
        collection_configuration={"hnsw": {"space": "cosine"}},
        create_collection_if_not_exists=create,
    )
