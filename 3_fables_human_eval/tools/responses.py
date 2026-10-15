"""Generate and freeze one response set for independent human review."""

from datetime import datetime

from models.config import (
    CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_NAME, EMBEDDING_MODEL,
    MODEL_NAME, PROJECT_ROOT,
)
from tools.results import fingerprint, read_json, write_json


def generate_responses(questions, ask_rag, k, prompt_text, label="baseline"):
    assert questions, "Load the questions first."
    assert len({row["id"] for row in questions}) == len(questions)
    sources = read_json(PROJECT_ROOT / "docs/dataset/fables.json")
    sources_by_id = {row["id"]: row for row in sources}
    rubric = read_json(PROJECT_ROOT / "docs/goldends/rubric.json")
    created_at = datetime.now().astimezone()
    run_id = "responses_" + created_at.strftime("%Y%m%d_%H%M%S_%f")
    responses = []

    for question in questions:
        result = ask_rag(question["question"])
        assert isinstance(result["answer"], str) and result["answer"].strip()
        responses.append({
            "question_id": question["id"],
            "type": question["type"],
            "question": question["question"],
            "fable_ids": question["fable_ids"],
            "source_fables": [sources_by_id[fid] for fid in question["fable_ids"]],
            "answer": result["answer"],
            "retrieved_context": result["retrieved_context"],
        })
        print(f"Answered {question['id']}", flush=True)

    run = {
        "response_run_id": run_id,
        "created_at": created_at.isoformat(),
        "completed_at": datetime.now().astimezone().isoformat(),
        "label": label,
        "model": MODEL_NAME,
        "temperature": 0,
        "reasoning_effort": "low",
        "max_tokens": 512,
        "k": k,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "embedding_model": EMBEDDING_MODEL,
        "collection": COLLECTION_NAME,
        "prompt_text": prompt_text,
        "prompt_hash": fingerprint(prompt_text),
        "questions_hash": fingerprint(questions),
        "source_hash": fingerprint(sources),
        "rubric_id": rubric["id"],
        "rubric_hash": fingerprint(rubric),
        "rubric": rubric,
        "responses": responses,
    }
    path = PROJECT_ROOT / "docs/evaluatedds" / f"{run_id}.json"
    write_json(path, run)
    return path
