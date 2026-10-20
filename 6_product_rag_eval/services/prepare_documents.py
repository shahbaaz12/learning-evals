"""Prepare one JSON document per product and explicitly index it in Chroma."""
import hashlib
import json

from langchain_core.documents import Document

from models.settings import DATA, EMBEDDING_MODEL, load_catalog


def prepare_documents(index=True):
    products = load_catalog()
    chunks = [Document(page_content=json.dumps(product, indent=2, ensure_ascii=False),
                       metadata={key: product[key] for key in
                                 ['product_id', 'product_name', 'category', 'subcategory', 'manufacturer']}
                       | {'source': 'Hierarchical_Product_Catalog.json'})
              for product in products]
    records = [dict(text=chunk.page_content, metadata=chunk.metadata) for chunk in chunks]
    (DATA / 'chunks.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    manifest = dict(products=len(chunks), embedding_model=EMBEDDING_MODEL,
                    document_prefix='search_document: ', query_prefix='search_query: ',
                    chunking='one product per chunk',
                    catalog_sha256=hashlib.sha256((DATA / 'Hierarchical_Product_Catalog.json').read_bytes()).hexdigest())
    if index:
        from models.vector_store import load_vector_store
        store = load_vector_store(create=True)
        expected_ids = [chunk.metadata['product_id'] for chunk in chunks]
        obsolete = set(store.get()['ids']) - set(expected_ids)
        if obsolete:
            store.delete(ids=sorted(obsolete))
        store.add_documents(documents=chunks, ids=expected_ids)
        (DATA / 'index_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print('Stored chunks:', len(store.get()['ids']))
    return chunks


if __name__ == '__main__':
    prepare_documents()
