"""Judge anonymous answer text; never expose student personas or reference marks."""

import json
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from models.config import MODEL_NAME, PROJECT_ROOT
from tools.evaluation import validate_marks
from tools.results import fingerprint, save_run


def grade_answer(model, question, answer_text, prompt_text):
    payload = {
        "question": question["question"],
        "maximum_marks": question["max_marks"],
        "reference_answer": question["reference_answer"],
        "rubric": question["dimensions"],
        "student_answer": answer_text,
    }
    response = model.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(content=json.dumps(payload, ensure_ascii=False)),
    ])
    grade = json.loads(response.content)
    grade["total_marks"] = sum(row["marks"] for row in grade["dimension_marks"])
    validate_marks(question, grade)
    return {
        "dimension_marks": grade["dimension_marks"],
        "total_marks": grade["total_marks"],
    }


def grade_all(model, questions, answers, prompt_text, label="baseline"):
    assert questions and answers
    assert len({row["id"] for row in answers}) == len(answers)
    question_by_id = {row["id"]: row for row in questions}
    started_at = datetime.now().astimezone().isoformat()
    grades = []
    for answer in answers:
        question = question_by_id[answer["question_id"]]
        grade = grade_answer(model, question, answer["answer"], prompt_text)
        grades.append({
            "answer_id": answer["id"],
            "question_id": answer["question_id"],
            **grade,
        })
        print(f"Graded {answer['id']}", flush=True)
    return save_run(PROJECT_ROOT / "docs/evaluatedds", "grades", {
        "started_at": started_at,
        "label": label,
        "model": MODEL_NAME,
        "temperature": 0,
        "reasoning_effort": "low",
        "max_tokens": 1024,
        "prompt_text": prompt_text,
        "prompt_hash": fingerprint(prompt_text),
        "questions_hash": fingerprint(questions),
        "answers_hash": fingerprint(answers),
        "grades": grades,
    })
