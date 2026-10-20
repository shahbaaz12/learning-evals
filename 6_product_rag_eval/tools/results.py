import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def save_retrieval_report(report, label, settings):
    project = Path(__file__).resolve().parents[1]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    catalog = project / "docs/dataset/Hierarchical_Product_Catalog.json"
    goldens = project / "docs/goldends/Hierarchical_RAG_Validation_Questions.json"

    saved_report = {
        **report,
        "experiment": label,
        "created_at": timestamp,
        "settings": settings,
        "catalog_sha256": hashlib.sha256(catalog.read_bytes()).hexdigest(),
        "goldens_sha256": hashlib.sha256(goldens.read_bytes()).hexdigest(),
    }

    destination = project / "docs/evalresults" / f"{label}_{timestamp}.json"
    destination.write_text(
        json.dumps(saved_report, indent=2),
        encoding="utf-8",
    )

    return destination


def load_artifact(label, outputs=False):
    project = Path(__file__).resolve().parents[1]
    meta = json.loads((project / 'docs/evalresults/latest_run.json').read_text(encoding='utf-8'))
    folder = 'evaluatedds' if outputs else 'evalresults'
    path = project / 'docs' / folder / f'{label}_{meta["run_id"]}.json'
    assert path.exists(), f'Missing saved report: {path.name}. See readme.md for the learning workflow.'
    return json.loads(path.read_text(encoding='utf-8'))


def load_first_baselines():
    project = Path(__file__).resolve().parents[1]
    reports = []
    for label in ['baseline_k3', 'candidate_k1']:
        path = sorted((project / 'docs/evalresults').glob(f'{label}_*.json'))[0]
        reports.append(json.loads(path.read_text(encoding='utf-8')))
    return reports


def quality_table(records, judgments):
    by_id = {row['id']: row for row in judgments}
    return [dict(id=row['id'], test_type=row['test_type'], status=row['status'],
                 citations=row['citations'], route=row['route'],
                 **({key: value for key, value in by_id[row['id']]['data'].items() if key != 'reasons'}
                    if by_id[row['id']]['ok'] else {})) for row in records]
