"""Read data, fingerprint an experiment, and save new JSON snapshots."""

import hashlib
import json
from datetime import datetime


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(value):
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_run(folder, prefix, data):
    now = datetime.now().astimezone()
    run_id = prefix + "_" + now.strftime("%Y%m%d_%H%M%S_%f")
    path = folder / f"{run_id}.json"
    folder.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        json.dump(
            {"run_id": run_id, "saved_at": now.isoformat(), **data},
            file, indent=2, ensure_ascii=False,
        )
    return path


def print_report(report, students):
    names = {student["id"]: student["name"] for student in students}
    print(f"Reference status: {report['reference_status']}")
    print(f"Answers compared: {report['answer_count']}")
    print(f"MAE: {report['mae']:.2f} marks per answer")
    print(f"Practice target <= {report['mae_target']:.2f}: {report['target_met']}")
    print("\nStudent | Reference total | Model total | MAE")
    for row in report["students"]:
        print(
            f"{names[row['student_id']]} | {row['reference_total']} | "
            f"{row['model_total']} | {row['mae']:.2f}"
        )
    print("\nAnswer | Reference | Model | Absolute error")
    for row in report["details"]:
        print(
            f"{row['answer_id']} | {row['reference_marks']} | "
            f"{row['model_marks']} | {row['absolute_error']}"
        )
