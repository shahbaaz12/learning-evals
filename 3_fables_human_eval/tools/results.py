"""Small JSON and reporting helpers."""

import hashlib
import json
from datetime import datetime

from models.config import PROJECT_ROOT


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(value):
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_report(report):
    stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S_%f")
    path = PROJECT_ROOT / "docs/evalresults" / f"combined_{stamp}.json"
    write_json(path, {"scored_at": datetime.now().astimezone().isoformat(), **report})
    return path


def print_report(report):
    print(f"Response run: {report['response_run_id']}")
    print(f"Questions: {report['question_count']} | Ratings: {report['rating_count']}")
    print(f"Combined helpfulness: {report['overall_mean']:.2f} / 5")
    for reviewer, mean in report["reviewer_means"].items():
        print(f"{reviewer}: {mean:.2f} / 5")
    print("\nQuestion | Jack | Jane | Jill | Mean | Spread")
    for row in report["details"]:
        scores = row["scores"]
        print(
            f"{row['question_id']} | {scores['Jack']} | {scores['Jane']} | "
            f"{scores['Jill']} | {row['mean']:.2f} | {row['spread']}"
        )
    print("\nQuestions to discuss:", ", ".join(report["disagreements"]) or "None")
