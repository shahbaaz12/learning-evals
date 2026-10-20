"""Translate supplied retrieval scopes into product IDs; never used by the RAG."""
import hashlib
import json

from models.settings import DATA, GOLDENS, load_catalog


def prepare_goldens():
    products = load_catalog()
    source = GOLDENS / 'Hierarchical_RAG_Validation_Questions.json'
    questions = json.loads(source.read_text(encoding='utf-8-sig'))['questions']
    aliases = {p['product_id']: p['product_id'] for p in products}
    for product in products:
        for variant in product['variants']:
            aliases[variant['variant_id']] = product['product_id']
    cases = []
    for question in questions:
        scope = question['expected_retrieval_scope']
        kind = question['test_type']
        if scope in aliases:
            ids = [aliases[scope]]
        elif kind == 'Category aggregation':
            ids = [p['product_id'] for p in products if p['category'] == scope]
        elif kind == 'Subcategory aggregation':
            ids = [p['product_id'] for p in products if p['subcategory'] == scope]
        elif kind == 'Cross-category comparison':
            ids = [p['product_id'] for p in products if p['manufacturer'].lower() in question['question'].lower()]
        else:
            # Catalog-wide evidence is our conservative reference for global,
            # ambiguity and absence questions. Other sufficient evidence sets may exist.
            ids = [p['product_id'] for p in products]
        assert ids, question['id']
        cases.append({**question, 'expected_product_ids': ids})
    document = dict(review_status='Supplied answers plus AI-prepared scope mapping; human review pending.',
                    catalog_sha256=hashlib.sha256((DATA / 'Hierarchical_Product_Catalog.json').read_bytes()).hexdigest(),
                    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), cases=cases)
    (GOLDENS / 'retrieval_cases.json').write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
    print(f'Saved {len(cases)} retrieval references, including variant-to-parent mappings.')


if __name__ == '__main__':
    prepare_goldens()
