"""Programmatic recall and precision evaluation for any value of k."""

from models.vector_store import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL


def evaluate_retriever(vector_store, goldens, k):
    """Retrieve each question and return per-question and average scores."""
    assert goldens, "The golden dataset must contain questions."
    assert k > 0, "k must be positive."
    results = []

    for case in goldens:
        retrieved = vector_store.similarity_search(case["question"], k=k)
        retrieved_ids = [chunk.metadata["chunk_id"] for chunk in retrieved]
        relevant_ids = set(case["relevant_chunk_ids"])
        returned_ids = set(retrieved_ids)
        assert relevant_ids, f"No relevant chunk IDs for {case['id']}."
        assert returned_ids, f"No chunks retrieved for {case['id']}."
        matched_ids = relevant_ids & returned_ids

        results.append({
            "id": case["id"],
            "question": case["question"],
            "relevant_chunk_ids": sorted(relevant_ids),
            "retrieved_chunk_ids": retrieved_ids,
            "missed_chunk_ids": sorted(relevant_ids - returned_ids),
            "recall": len(matched_ids) / len(relevant_ids),
            "precision": len(matched_ids) / len(returned_ids),
        })

    return {
        "k": k,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "embedding_model": EMBEDDING_MODEL,
        "question_count": len(results),
        "average_recall": sum(row["recall"] for row in results) / len(results),
        "average_precision": sum(row["precision"] for row in results) / len(results),
        "results": results,
    }
