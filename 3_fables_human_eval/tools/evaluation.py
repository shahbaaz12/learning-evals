"""Combine completed, independent human ratings. No model judge is used."""

from models.config import REVIEWERS


def combine_scores(run, reviews):
    question_ids = [row["question_id"] for row in run["responses"]]
    assert question_ids and len(question_ids) == len(set(question_ids))
    assert len(reviews) == len(REVIEWERS), "Load all three rating sheets."
    assert {review["rater"] for review in reviews} == set(REVIEWERS)
    by_reviewer = {}

    for review in reviews:
        assert review["response_run_id"] == run["response_run_id"], "Use the same response run."
        assert review["rubric_id"] == run["rubric_id"], "Use the same rubric."
        assert review["rubric_hash"] == run["rubric_hash"], "The rubric changed."
        rows = review["ratings"]
        assert len(rows) == len(question_ids), "Every question needs one rating."
        assert {row["question_id"] for row in rows} == set(question_ids), "Question IDs must match."
        for row in rows:
            assert type(row["score"]) is int and 1 <= row["score"] <= 5, (
                f"{review['rater']} / {row['question_id']}: enter a score from 1 to 5."
            )
            assert isinstance(row["reason"], str) and row["reason"].strip(), (
                f"{review['rater']} / {row['question_id']}: enter a reason."
            )
        by_reviewer[review["rater"]] = {row["question_id"]: row for row in rows}

    details = []
    for question_id in question_ids:
        ratings = {name: by_reviewer[name][question_id] for name in REVIEWERS}
        scores = {name: row["score"] for name, row in ratings.items()}
        details.append({
            "question_id": question_id,
            "scores": scores,
            "reasons": {name: row["reason"] for name, row in ratings.items()},
            "mean": sum(scores.values()) / len(REVIEWERS),
            "spread": max(scores.values()) - min(scores.values()),
        })

    return {
        "response_run_id": run["response_run_id"],
        "rubric_id": run["rubric_id"],
        "rubric_hash": run["rubric_hash"],
        "question_count": len(question_ids),
        "rating_count": len(question_ids) * len(REVIEWERS),
        "overall_mean": sum(row["mean"] for row in details) / len(details),
        "reviewer_means": {
            name: sum(row["score"] for row in by_reviewer[name].values()) / len(question_ids)
            for name in REVIEWERS
        },
        "disagreements": [row["question_id"] for row in details if row["spread"] >= 2],
        "details": details,
    }
