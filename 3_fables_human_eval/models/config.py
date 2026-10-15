"""Settings shared by preparation, the RAG, and saved reports."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "human_eval_fables"
MODEL_NAME = "openai/gpt-oss-120b"
DEFAULT_K = 5
REVIEWERS = ("Jack", "Jane", "Jill")
