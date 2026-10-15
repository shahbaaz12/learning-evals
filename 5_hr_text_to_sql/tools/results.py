import hashlib
import json
from datetime import datetime, timezone

from models.settings import DATABASE, PROJECT


def save_run(label, records, summary, settings):
    label = label.replace('/', '_')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = PROJECT / 'docs/evaluatedds' / f'{stamp}_{label}.json'
    output.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    report = dict(created_at=stamp, label=label, summary=summary, settings=settings,
                  database_sha256=hashlib.sha256(DATABASE.read_bytes()).hexdigest(),
                  prompt_sha256=hashlib.sha256((PROJECT / 'prompts/text_to_sql.md').read_bytes()).hexdigest(),
                  predictions=output.name)
    destination = PROJECT / 'docs/evalresults' / f'{stamp}_{label}.json'
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return destination


def load_latest_reports(models):
    reports = []
    for model in models:
        label = model['model_id'].replace('/', '_')
        paths = sorted((PROJECT / 'docs/evalresults').glob(f'*_{label}.json'))
        assert paths, f'Run the evaluation for {model["name"]} first.'
        report = json.loads(paths[-1].read_text(encoding='utf-8'))
        assert report['database_sha256'] == hashlib.sha256(DATABASE.read_bytes()).hexdigest()
        assert report['prompt_sha256'] == hashlib.sha256((PROJECT / 'prompts/text_to_sql.md').read_bytes()).hexdigest()
        assert report['settings']['model'] == model, 'Model settings changed; run a new evaluation.'
        reports.append(dict(report_file=paths[-1].name, **report))
    return reports


def save_comparison(reports):
    rows = [report['summary'] for report in reports]
    rows.sort(key=lambda row: (-row['accuracy'], row['projected_monthly_inr'], row['mean_seconds']))
    document = dict(reports=[r['report_file'] for r in reports], summaries=rows,
                    note='Actual six-question API runs. Monthly projections use reported tokens, standard uncached rates, 30,000 requests/month, INR 95/USD and 20% reserve. Estimates are not invoices.')
    path = PROJECT / 'docs/evalresults' / 'live_comparison.json'
    path.write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
    return rows
