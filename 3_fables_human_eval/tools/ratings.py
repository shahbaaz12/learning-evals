"""Create rating sheets and collect real human scores in small batches."""

import json
from datetime import datetime

from models.config import PROJECT_ROOT, REVIEWERS
from tools.results import read_json, write_json


def rating_folder(run):
    return PROJECT_ROOT / "docs/ratings" / run["response_run_id"]


def prepare_ratings(run):
    paths = []
    for reviewer in REVIEWERS:
        path = rating_folder(run) / f"{reviewer.lower()}.json"
        if not path.exists():
            write_json(path, {
                "rater": reviewer,
                "response_run_id": run["response_run_id"],
                "rubric_id": run["rubric_id"],
                "rubric_hash": run["rubric_hash"],
                "ratings": [
                    {"question_id": row["question_id"], "score": None,
                     "reason": None, "rated_at": None}
                    for row in run["responses"]
                ],
            })
        sheet = read_json(path)
        assert sheet["rater"] == reviewer
        assert sheet["response_run_id"] == run["response_run_id"]
        assert sheet["rubric_hash"] == run["rubric_hash"]
        paths.append(path)
    return paths


def rating_progress(run):
    progress = {}
    for path in prepare_ratings(run):
        sheet = read_json(path)
        progress[sheet["rater"]] = sum(
            type(row["score"]) is int and 1 <= row["score"] <= 5
            and isinstance(row["reason"], str) and bool(row["reason"].strip())
            for row in sheet["ratings"]
        )
    return progress


def show_case(run, question_id):
    case = next(row for row in run["responses"] if row["question_id"] == question_id)
    print(f"\n{case['question_id']}: {case['question']}\n")
    for fable in case["source_fables"]:
        print(f"REFERENCE: {fable['title']} [page {fable['page']}]")
        print(fable["text"], "\n")
    print("CHATBOT ANSWER:\n" + case["answer"])
    return case


def rate_answers(run, reviewer, batch_size=5):
    assert reviewer in REVIEWERS, "Choose Jack, Jane, or Jill."
    assert type(batch_size) is int and batch_size > 0
    prepare_ratings(run)
    path = rating_folder(run) / f"{reviewer.lower()}.json"
    sheet = read_json(path)
    pending = [row for row in sheet["ratings"] if row["score"] is None]

    for row in pending[:batch_size]:
        show_case(run, row["question_id"])
        score = int(input(f"\n{reviewer}'s helpfulness score (1-5): "))
        assert 1 <= score <= 5, "Use an integer from 1 to 5."
        reason = input("Brief reason: ").strip()
        assert reason, "Explain the rating briefly."
        row.update(score=score, reason=reason,
                   rated_at=datetime.now().astimezone().isoformat())
        path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved {row['question_id']} for {reviewer}.")

    completed = sum(row["score"] is not None for row in sheet["ratings"])
    print(f"Completed: {completed}/{len(sheet['ratings'])}")
    return path
