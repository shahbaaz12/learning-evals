"""Validate rubric marks and compare the judge with reference grades."""

from models.config import MAE_TARGET
from tools.results import fingerprint


def validate_marks(question, grade):
    dimensions = {row["id"]: row for row in question["dimensions"]}
    rows = grade["dimension_marks"]
    assert len(rows) == len(dimensions), "Grade every dimension once."
    assert {row["dimension_id"] for row in rows} == set(dimensions), "Dimension IDs must match."
    for row in rows:
        assert type(row["marks"]) is int, "Marks must be integers."
        assert 0 <= row["marks"] <= dimensions[row["dimension_id"]]["max_marks"]
        assert isinstance(row["reason"], str) and row["reason"].strip()
    assert type(grade["total_marks"]) is int
    assert grade["total_marks"] == sum(row["marks"] for row in rows), "Incorrect total."
    assert 0 <= grade["total_marks"] <= question["max_marks"]


def validate_dataset(questions, students, answers, references):
    assert questions and students and answers and references
    question_by_id = {row["id"]: row for row in questions}
    student_ids = {row["id"] for row in students}
    assert len(question_by_id) == len(questions), "Duplicate question IDs."
    assert len(student_ids) == len(students), "Duplicate student IDs."
    answer_by_id = {row["id"]: row for row in answers}
    assert len(answer_by_id) == len(answers), "Duplicate answer IDs."
    for question in questions:
        dimensions = question["dimensions"]
        assert len({row["id"] for row in dimensions}) == len(dimensions)
        assert all(type(row["max_marks"]) is int and row["max_marks"] > 0 for row in dimensions)
        assert sum(row["max_marks"] for row in dimensions) == question["max_marks"]
    expected_pairs = {(student, question) for student in student_ids for question in question_by_id}
    pairs = {(row["student_id"], row["question_id"]) for row in answers}
    assert pairs == expected_pairs and len(answers) == len(expected_pairs), "One answer per student/question."
    assert all(isinstance(row["answer"], str) and row["answer"].strip() for row in answers)
    assert len(references) == len(answers), "Reference grades must cover all answers."
    assert {row["answer_id"] for row in references} == set(answer_by_id)
    for grade in references:
        answer = answer_by_id[grade["answer_id"]]
        assert grade["question_id"] == answer["question_id"]
        validate_marks(question_by_id[answer["question_id"]], grade)


def compare_grades(questions, students, answers, references, model_run, reference_metadata):
    validate_dataset(questions, students, answers, references)
    assert model_run["questions_hash"] == fingerprint(questions), "Question/rubric version changed."
    assert model_run["answers_hash"] == fingerprint(answers), "Student answers changed."
    if reference_metadata.get("rubric_hash"):
        assert reference_metadata["rubric_hash"] == fingerprint(questions)
    if reference_metadata.get("answers_hash"):
        assert reference_metadata["answers_hash"] == fingerprint(answers)
    question_by_id = {row["id"]: row for row in questions}
    answer_by_id = {row["id"]: row for row in answers}
    reference_by_id = {row["answer_id"]: row for row in references}
    grades = model_run["grades"]
    assert len(grades) == len(answers), "All answers must be model-graded."
    assert {row["answer_id"] for row in grades} == set(answer_by_id), "Model answer IDs must match."

    details = []
    for grade in grades:
        answer = answer_by_id[grade["answer_id"]]
        assert grade["question_id"] == answer["question_id"]
        validate_marks(question_by_id[answer["question_id"]], grade)
        reference = reference_by_id[grade["answer_id"]]
        details.append({
            "answer_id": grade["answer_id"],
            "student_id": answer["student_id"],
            "question_id": answer["question_id"],
            "reference_marks": reference["total_marks"],
            "model_marks": grade["total_marks"],
            "absolute_error": abs(grade["total_marks"] - reference["total_marks"]),
            "model_dimension_marks": grade["dimension_marks"],
            "reference_dimension_marks": reference["dimension_marks"],
        })

    student_summary = []
    for student in students:
        rows = [row for row in details if row["student_id"] == student["id"]]
        student_summary.append({
            "student_id": student["id"],
            "reference_total": sum(row["reference_marks"] for row in rows),
            "model_total": sum(row["model_marks"] for row in rows),
            "mae": sum(row["absolute_error"] for row in rows) / len(rows),
        })
    mae = sum(row["absolute_error"] for row in details) / len(details)
    return {
        "model_run_id": model_run["run_id"],
        "reference_status": reference_metadata["status"],
        "reference_hash": fingerprint(references),
        "questions_hash": fingerprint(questions),
        "answers_hash": fingerprint(answers),
        "answer_count": len(details),
        "mae": mae,
        "mae_target": MAE_TARGET,
        "target_met": mae <= MAE_TARGET,
        "students": student_summary,
        "details": details,
    }
