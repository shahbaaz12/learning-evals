"""Save and print evaluation runs without repeating notebook code."""

import json
from datetime import datetime

from models.vector_store import PROJECT_ROOT


def save_results(run, label="run"):
    """Save a timestamped report and return its path."""
    saved_at = datetime.now().astimezone()
    snapshot = {"saved_at": saved_at.isoformat(), **run}
    folder = PROJECT_ROOT / "docs/evalresults"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (
        f"{label}_k{run['k']}_{saved_at.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )
    with path.open("x", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)
    return path


def print_results(run):
    """Display per-question scores and the overall averages."""
    print(f"Evaluation at k={run['k']}")
    for row in run["results"]:
        print(
            f"{row['id']} | Recall: {row['recall']:.2f}"
            f" | Precision: {row['precision']:.2f}"
        )
    print(f"\nQuestions evaluated: {run['question_count']}")
    print(f"Average Recall@{run['k']}: {run['average_recall']:.2%}")
    print(f"Average Precision@{run['k']}: {run['average_precision']:.2%}")


def print_comparison(baseline, candidate):
    """Compare two runs without assuming particular values of k."""
    baseline_by_id = {row["id"]: row for row in baseline["results"]}
    candidate_ids = {row["id"] for row in candidate["results"]}
    assert set(baseline_by_id) == candidate_ids, "Compare the same question IDs."

    for row in candidate["results"]:
        old = baseline_by_id[row["id"]]
        print(
            f"{row['id']} | Recall@{baseline['k']}: {old['recall']:.2f}"
            f" | Recall@{candidate['k']}: {row['recall']:.2f}"
        )

    print("\nk | Average recall | Average precision")
    for run in (baseline, candidate):
        print(
            f"{run['k']} | {run['average_recall']:.2%}"
            f" | {run['average_precision']:.2%}"
        )
    recall_change = candidate["average_recall"] - baseline["average_recall"]
    precision_change = candidate["average_precision"] - baseline["average_precision"]
    print(f"\nRecall change: {recall_change * 100:+.2f} percentage points")
    print(f"Precision change: {precision_change * 100:+.2f} percentage points")


def print_misses(run):
    """Optionally inspect missed reference chunks for an existing run."""
    incomplete = [row for row in run["results"] if row["missed_chunk_ids"]]
    print(f"Questions with missed chunks: {len(incomplete)}")
    for row in incomplete:
        print(f"\n{row['id']} | Recall@{run['k']}: {row['recall']:.2f}")
        print(f"Question: {row['question']}")
        print(f"Relevant IDs: {row['relevant_chunk_ids']}")
        print(f"Retrieved IDs: {row['retrieved_chunk_ids']}")
        print(f"Missed IDs: {row['missed_chunk_ids']}")
        print("-" * 60)
