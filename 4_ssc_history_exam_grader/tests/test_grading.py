"""Synthetic fixtures verify scoring arithmetic and blind model inputs."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from tools.evaluation import compare_grades, validate_dataset, validate_marks
from tools.grading import grade_answer
from tools.results import fingerprint


def fixture_data():
    question = {
        "id": "q001", "question": "Test question", "max_marks": 4,
        "reference_answer": "Test reference",
        "dimensions": [
            {"id": "d1", "criterion": "Point one", "max_marks": 2},
            {"id": "d2", "criterion": "Point two", "max_marks": 2},
        ],
    }
    students = [{"id": "jack", "name": "Jack"}, {"id": "jane", "name": "Jane"}]
    answers = [
        {"id": name + "_q001", "student_id": name, "question_id": "q001", "answer": "Test answer"}
        for name in ("jack", "jane")
    ]
    def grade(answer_id, marks):
        return {
            "answer_id": answer_id, "question_id": "q001",
            "dimension_marks": [
                {"dimension_id": f"d{i+1}", "marks": mark, "reason": "Test fixture."}
                for i, mark in enumerate(marks)
            ],
            "total_marks": sum(marks),
        }
    references = [grade("jack_q001", [2, 2]), grade("jane_q001", [1, 0])]
    run = {
        "run_id": "test_only", "questions_hash": fingerprint([question]),
        "answers_hash": fingerprint(answers),
        "grades": [grade("jack_q001", [2, 2]), grade("jane_q001", [1, 2])],
    }
    return [question], students, answers, references, run, {"status": "simulated_pending_human_review"}


def test_mae_is_average_answer_error():
    data = fixture_data()
    report = compare_grades(*data)
    assert report["mae"] == 1
    assert [row["absolute_error"] for row in report["details"]] == [0, 2]
    assert report["students"][0]["reference_total"] == 4
    assert report["students"][1]["model_total"] == 3
    assert report["reference_status"] == "simulated_pending_human_review"


@pytest.mark.parametrize("mark", [-1, 3, 1.5, True, None])
def test_invalid_dimension_marks_are_rejected(mark):
    questions, _, _, references, _, _ = fixture_data()
    grade = deepcopy(references[0])
    grade["dimension_marks"][0]["marks"] = mark
    with pytest.raises(AssertionError):
        validate_marks(questions[0], grade)


def test_wrong_total_is_rejected():
    questions, _, _, references, _, _ = fixture_data()
    grade = deepcopy(references[0])
    grade["total_marks"] = 1
    with pytest.raises(AssertionError):
        validate_marks(questions[0], grade)


def test_duplicate_model_answer_is_rejected():
    data = fixture_data()
    data[4]["grades"][1] = deepcopy(data[4]["grades"][0])
    with pytest.raises(AssertionError):
        compare_grades(*data)


def test_missing_student_answer_is_rejected():
    questions, students, answers, references, _, _ = fixture_data()
    with pytest.raises(AssertionError):
        validate_dataset(questions, students, answers[:1], references)


@pytest.mark.parametrize("field", ["questions_hash", "answers_hash"])
def test_mixed_versions_are_rejected(field):
    data = fixture_data()
    data[4][field] = "different_version"
    with pytest.raises(AssertionError):
        compare_grades(*data)


def test_judge_input_is_anonymous_and_total_is_computed():
    questions, _, _, _, _, _ = fixture_data()
    captured = []
    def invoke(messages):
        captured.extend(messages)
        return SimpleNamespace(content='{"dimension_marks":[{"dimension_id":"d1","marks":2,"reason":"Test"},{"dimension_id":"d2","marks":1,"reason":"Test"}],"total_marks":99}')
    model = SimpleNamespace(invoke=invoke)
    grade = grade_answer(model, questions[0], "Anonymous test answer.", "Use the rubric.")
    assert grade["total_marks"] == 3
    payload = captured[1].content
    assert "Anonymous test answer." in payload
    assert all(word not in payload for word in ["Jack", "Jane", "persona", "reference_marks", "student_id"])


def test_reference_fingerprint_is_checked():
    data = fixture_data()
    data[5]["answers_hash"] = "not_the_same_answers"
    with pytest.raises(AssertionError):
        compare_grades(*data)
