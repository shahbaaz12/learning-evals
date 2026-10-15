"""Open the saved Chroma collection without rebuilding it."""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from models.config import COLLECTION_NAME, EMBEDDING_MODEL, PROJECT_ROOT


def load_vector_store(create=False):
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
