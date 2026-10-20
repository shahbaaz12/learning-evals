from langchain_huggingface import HuggingFaceEmbeddings
from models.settings import EMBEDDING_MODEL


def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True,
            "prompt": "search_document: ",
        },
        query_encode_kwargs={
            "normalize_embeddings": True,
            "prompt": "search_query: ",
        },
    )


if __name__ == "__main__":
    embeddings = load_embeddings()
    vector = embeddings.embed_query("What is AeroTherm X1?")
    print("Embedding dimensions:", len(vector))
