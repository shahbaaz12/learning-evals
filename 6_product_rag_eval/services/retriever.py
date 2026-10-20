"""Compare plain semantic search with a small catalog-aware retrieval rule."""
from langchain_core.documents import Document

from models.settings import load_catalog


def fetch_products(store, ids):
    result = store.get(ids=ids)
    by_id = {key: Document(page_content=text, metadata=meta)
             for key, text, meta in zip(result['ids'], result['documents'], result['metadatas'])}
    assert set(ids) <= set(by_id), 'Rebuild the store; catalog products are missing.'
    return [by_id[key] for key in ids]


def retrieve(store, question, k=1, mode='semantic'):
    assert mode in ['semantic', 'catalog'] and k > 0
    if mode == 'semantic':
        return store.similarity_search(question, k=k), 'semantic'
    products = load_catalog()
    query = question.lower()
    named = [p for p in products if p['product_name'].lower() in query]
    if len(named) > 1:
        return fetch_products(store, [p['product_id'] for p in named]), 'named_products'
    broad = not named and any(word in query for word in ['all ', 'which products', 'compare', 'categories', 'several products', 'which product'])
    if broad:
        for field in ['manufacturer', 'subcategory', 'category']:
            values = [value for value in sorted({p[field] for p in products}) if value.lower() in query]
            if values:
                ids = [p['product_id'] for p in products if p[field] in values]
                return fetch_products(store, ids), field
        return fetch_products(store, [p['product_id'] for p in products]), 'whole_catalog'
    return store.similarity_search(question, k=k), 'semantic'
