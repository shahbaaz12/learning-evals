"""Offline checks of the simple RAG's references, retrieval routes and inputs."""
import ast
import json
from types import SimpleNamespace

from langchain_core.documents import Document

from models.settings import DATA, PROJECT, load_catalog
from services.retriever import retrieve
from tools.retrieval_eval import load_cases


def verify():
    products = load_catalog()
    cases = load_cases()
    assert len(products) == 20 and len(cases) == 78
    by_id = {p['product_id']: p for p in products}
    assert len(by_id) == 20
    assert next(c for c in cases if c['id'] == 'Q3')['expected_product_ids'] == ['HCL-101']
    for case in cases:
        assert set(case['expected_product_ids']) <= set(by_id)
    documents = {p['product_id']: Document(page_content=json.dumps(p), metadata={'product_id': p['product_id']}) for p in products}
    def get(ids):
        return dict(ids=ids, documents=[documents[key].page_content for key in ids],
                    metadatas=[documents[key].metadata for key in ids])
    store = SimpleNamespace(get=get, similarity_search=lambda question, k: list(documents.values())[:k])
    selected, route = retrieve(store, 'List all products under the Home Appliances category.', mode='catalog')
    assert route == 'category' and len(selected) == 6
    selected, route = retrieve(store, 'Which products belong to the Cleaning subcategory?', mode='catalog')
    assert route == 'subcategory' and {d.metadata['product_id'] for d in selected} == {'APC-901', 'APC-902'}
    selected, route = retrieve(store, 'Compare the products manufactured by Meridian Workplace with Northline Mobility.', mode='catalog')
    assert route == 'manufacturer' and len(selected) == 8
    selected, route = retrieve(store, 'Which product has a variant called Enterprise?', mode='catalog')
    assert route == 'whole_catalog' and len(selected) == 20
    selected, route = retrieve(store, 'What is the price of AeroTherm X1?', mode='catalog')
    assert route == 'semantic' and len(selected) == 1
    for path in PROJECT.rglob('*.py'):
        assert not any(isinstance(node, (ast.Try, ast.ClassDef)) for node in ast.walk(ast.parse(path.read_text(encoding='utf-8')))), path
    chunks = json.loads((DATA / 'chunks.json').read_text(encoding='utf-8'))
    assert len(chunks) == 20
    assert all('expected_answer' not in row['text'] for row in chunks)
    print('Offline checks passed: 78 references, variant mapping, group/global routing, no label leakage, no try/except or custom classes.')


if __name__ == '__main__':
    verify()
