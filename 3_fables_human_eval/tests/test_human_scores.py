"""Synthetic fixtures test the scorer; they are never saved as human ratings."""

from copy import deepcopy

import pytest

from tools.evaluation import combine_scores


def example():
    run = {
        "response_run_id": "test_only",
        "rubric_id": "helpfulness_v1",
        "rubric_hash": "test_rubric",
        "responses": [{"question_id": "h001"}, {"question_id": "h002"}],
    }
    reviews = []
    for name, scores in [("Jack", [4, 2]), ("Jane", [3, 4]), ("Jill", [5, 3])]:
        reviews.append({
            "rater": name,
            "response_run_id": run["response_run_id"],
            "rubric_id": run["rubric_id"],
            "rubric_hash": run["rubric_hash"],
            "ratings": [
                {"question_id": question["question_id"], "score": score,
                 "reason": "Synthetic test fixture."}
                for question, score in zip(run["responses"], scores)
            ],
        })
    return run, reviews


def test_equal_weighting_and_disagreement():
    run, reviews = example()
    report = combine_scores(run, reviews)
    assert report["overall_mean"] == 3.5
    assert [row["mean"] for row in report["details"]] == [4, 3]
    assert report["reviewer_means"] == {"Jack": 3, "Jane": 3.5, "Jill": 4}
    assert report["rating_count"] == 6
    assert report["disagreements"] == ["h001", "h002"]


@pytest.mark.parametrize("score", [None, 0, 6, 3.5, True, "4"])
def test_missing_or_invalid_scores_are_rejected(score):
    run, reviews = example()
    reviews[0]["ratings"][0]["score"] = score
    with pytest.raises(AssertionError):
        combine_scores(run, reviews)


@pytest.mark.parametrize("field,value", [
    ("response_run_id", "different_run"),
    ("rubric_id", "different_rubric"),
    ("rubric_hash", "changed_rubric"),
])
def test_mixed_runs_or_rubrics_are_rejected(field, value):
    run, reviews = example()
    reviews[1][field] = value
    with pytest.raises(AssertionError):
        combine_scores(run, reviews)


def test_duplicate_question_ids_are_rejected():
    run, reviews = example()
    reviews[0]["ratings"][1]["question_id"] = "h001"
    with pytest.raises(AssertionError):
        combine_scores(run, reviews)


def test_missing_reason_is_rejected():
    run, reviews = example()
    reviews[0]["ratings"][0]["reason"] = " "
    with pytest.raises(AssertionError):
        combine_scores(run, reviews)


def test_missing_reviewer_is_rejected():
    run, reviews = example()
    with pytest.raises(AssertionError):
        combine_scores(run, reviews[:2])


def test_ratings_are_not_modified():
    run, reviews = example()
    before = deepcopy(reviews)
    combine_scores(run, reviews)
    assert reviews == before


def test_rating_collection_resumes_without_resetting_scores(tmp_path, monkeypatch):
    from tools import ratings
    from tools.results import read_json

    monkeypatch.setattr(ratings, "PROJECT_ROOT", tmp_path)
    run, _ = example()
    for row in run["responses"]:
        row.update(question="Test question", answer="Test answer", source_fables=[])

    answers = iter(["4", "Synthetic test reason."])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    path = ratings.rate_answers(run, "Jack", batch_size=1)
    before = read_json(path)

    ratings.prepare_ratings(run)
    assert read_json(path) == before
    assert ratings.rating_progress(run) == {"Jack": 1, "Jane": 0, "Jill": 0}
    assert before["ratings"][1]["score"] is None
