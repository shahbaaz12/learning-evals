from langchain_chroma import Chroma
from models.embeddings import load_embeddings
from models.settings import COLLECTION, PROJECT

project = PROJECT


def load_vector_store(create=False):
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=load_embeddings(),
        persist_directory=str(project / "chroma_store"),
        collection_configuration={"hnsw": {"space": "cosine"}},
        create_collection_if_not_exists=create,
    )


if __name__ == "__main__":
    store = load_vector_store(create=True)
    print("Stored chunks:", len(store.get()["ids"]))
