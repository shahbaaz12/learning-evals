def evaluate_retrieval(store, questions, k=3):
    assert k > 0

    supported_types = [
        "Local product lookup",
        "Leaf / error-code lookup",
    ]

    cases = [
        question for question in questions if question["test_type"] in supported_types
    ]
    assert cases, "No supported questions found."

    results = []

    for case in cases:
        matches = store.similarity_search(case["question"], k=k)
        retrieved_ids = [match.metadata["product_id"] for match in matches]

        expected_id = case["expected_retrieval_scope"]
        found = int(expected_id in retrieved_ids)

        results.append(
            {
                "id": case["id"],
                "question": case["question"],
                "expected_id": expected_id,
                "retrieved_ids": retrieved_ids,
                "recall": found,
                "precision": found / len(retrieved_ids) if retrieved_ids else 0,
            }
        )

    return {
        "k": k,
        "questions_evaluated": len(results),
        "recall_at_k": sum(row["recall"] for row in results) / len(results),
        "precision_at_k": sum(row["precision"] for row in results) / len(results),
        "results": results,
    }


def load_cases():
    import hashlib
    import json
    from models.settings import DATA, GOLDENS
    document = json.loads((GOLDENS / 'retrieval_cases.json').read_text(encoding='utf-8'))
    assert document['catalog_sha256'] == hashlib.sha256((DATA / 'Hierarchical_Product_Catalog.json').read_bytes()).hexdigest(), 'Regenerate references after catalog changes.'
    assert document['source_sha256'] == hashlib.sha256((GOLDENS / 'Hierarchical_RAG_Validation_Questions.json').read_bytes()).hexdigest(), 'Regenerate references after golden-question changes.'
    return document['cases']


def evaluate_all_retrieval(store, cases, k=1, mode='semantic'):
    from services.retriever import retrieve
    rows = []
    for case in cases:
        documents, route = retrieve(store, case['question'], k=k, mode=mode)
        retrieved = [d.metadata['product_id'] for d in documents]
        expected = set(case['expected_product_ids'])
        hits = len(expected & set(retrieved))
        rows.append(dict(id=case['id'], test_type=case['test_type'], question=case['question'],
                         expected_ids=sorted(expected), retrieved_ids=retrieved, route=route,
                         recall=hits / len(expected), precision=hits / len(retrieved) if retrieved else 0,
                         all_evidence_found=expected <= set(retrieved)))
    return dict(k=k, mode=mode, questions_evaluated=len(rows),
                recall_at_k=sum(r['recall'] for r in rows) / len(rows),
                precision_at_k=sum(r['precision'] for r in rows) / len(rows),
                full_evidence_rate=sum(r['all_evidence_found'] for r in rows) / len(rows),
                note='In catalog mode k applies only to semantic fallback; metadata/catalog routes return all selected products.', results=rows)
