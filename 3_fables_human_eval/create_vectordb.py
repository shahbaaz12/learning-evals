import json

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.config import CHUNK_OVERLAP, CHUNK_SIZE, PROJECT_ROOT
from models.vector_store import load_vector_store


def create_vectordb():
    # 1. Load each fable page, skipping the cover.
    pdf_path = PROJECT_ROOT / "docs/dataset/Classic_Fables_Collection.pdf"
    reader = PdfReader(pdf_path)

    documents = [
        Document(
            page_content=page.extract_text(),
            metadata={"source": pdf_path.name, "page": page_number},
        )
        for page_number, page in enumerate(reader.pages[1:], start=2)
    ]

    # 2. Split the documents into searchable passages.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{pdf_path.stem}:{chunk.metadata['page']}:{index}"

    records = [
        {"text": chunk.page_content, "metadata": chunk.metadata}
        for chunk in chunks
    ]
    (PROJECT_ROOT / "docs/dataset/chunks.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # 3. Embed and save the chunks in Chroma.
    vector_store = load_vector_store(create=True)
    vector_store.add_documents(
        documents=chunks,
        ids=[chunk.metadata["chunk_id"] for chunk in chunks],
    )

    print(f"Fable pages: {len(documents)}")
    print(f"Chunks indexed: {len(chunks)}")
    print(f"Database: {PROJECT_ROOT / 'chroma_store'}")


if __name__ == "__main__":
    create_vectordb()
