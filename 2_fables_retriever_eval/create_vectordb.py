"""Read the PDF, prepare 600/100 chunks, and add them to Chroma."""

import json

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from models.vector_store import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    PROJECT_ROOT,
    load_vector_store,
)


def create_vectordb():
    pdf_path = PROJECT_ROOT / "docs/dataset/Classic_Fables_Collection.pdf"
    reader = PdfReader(pdf_path)
    documents = []

    # Skip the cover; keep the original PDF page numbers.
    for page_number, page in enumerate(reader.pages[1:], start=2):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(Document(
                page_content=text,
                metadata={"source": pdf_path.name, "page": page_number},
            ))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = (
            f"{pdf_path.stem}:{chunk.metadata['page']}:{index}"
        )

    chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
    records = [
        {"text": chunk.page_content, "metadata": chunk.metadata}
        for chunk in chunks
    ]
    chunks_path = PROJECT_ROOT / "docs/dataset/chunks.json"
    chunks_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    vector_store = load_vector_store(create=True)
    vector_store.add_documents(documents=chunks, ids=chunk_ids)

    print(f"Fable pages: {len(documents)}")
    print(f"Chunks indexed: {len(chunks)}")
    print(f"Chunk reference: {chunks_path}")
    return vector_store


if __name__ == "__main__":
    create_vectordb()
