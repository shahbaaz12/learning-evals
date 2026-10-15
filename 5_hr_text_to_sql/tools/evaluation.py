import hashlib
import json
import subprocess
import sys
from collections import Counter
from time import perf_counter, sleep

from models.settings import DATA, DATABASE, PROJECT


def load_goldens():
    document = json.loads((PROJECT / 'docs/goldends/goldens.json').read_text(encoding='utf-8'))
    assert document['database_sha256'] == hashlib.sha256(DATABASE.read_bytes()).hexdigest(), 'Database changed; inspect the change and regenerate goldens.'
    assert document['seed_sha256'] == hashlib.sha256((DATA / 'seed.json').read_bytes()).hexdigest(), 'Regenerate goldens after changing the seed.'
    assert document['schema_sha256'] == hashlib.sha256((DATA / 'schema.sql').read_bytes()).hexdigest(), 'Regenerate goldens after changing the schema.'
    return document['cases']


def execute_sql(sql):
    process = subprocess.run([sys.executable, str(PROJECT / 'tools/sql_worker.py'), str(DATABASE)],
                             input=sql, text=True, capture_output=True, timeout=10)
    if process.returncode:
        return dict(columns=[], rows=[], error=process.stderr.strip().splitlines()[-1])
    return dict(**json.loads(process.stdout), error=None)


def same_answer(actual, expected):
    if actual.get('error') or len(actual['columns']) != len(expected['columns']):
        return False
    # Ignore alias names, keep column order, row multiplicity, NULL and text.
    # Float rounding only removes tiny SQLite representation differences.
    def normalized(rows):
        return [tuple(round(v, 6) if isinstance(v, float) else v for v in row) for row in rows]
    left, right = normalized(actual['rows']), normalized(expected['rows'])
    return left == right if expected['order_matters'] else Counter(left) == Counter(right)


def evaluate(cases, generate, request_pause_seconds=0):
    records = []
    for case in cases:
        if records and request_pause_seconds:
            sleep(request_pause_seconds)  # Batch pacing is outside single-request latency.
        started = perf_counter()
        response = generate(case['question'])
        generated_seconds = perf_counter() - started
        actual = execute_sql(response['sql'])
        records.append(dict(id=case['id'], difficulty=case['difficulty'],
                            question=case['question'], **response, actual=actual,
                            expected=dict(columns=case['columns'], rows=case['rows']),
                            correct=same_answer(actual, case),
                            generation_seconds=round(generated_seconds, 4),
                            end_to_end_seconds=round(perf_counter() - started, 4)))
    return records


def summarize(records, model, budget):
    from tools.budget import monthly_cost
    n = len(records)
    return dict(model=model['name'], questions=n,
                accuracy=sum(r['correct'] for r in records) / n,
                sql_errors=sum(bool(r['actual']['error']) for r in records),
                mean_seconds=sum(r['end_to_end_seconds'] for r in records) / n,
                by_difficulty={difficulty: sum(r['correct'] for r in records if r['difficulty'] == difficulty) / sum(r['difficulty'] == difficulty for r in records)
                               for difficulty in sorted({r['difficulty'] for r in records})},
                estimated_run_usd=sum((r['input_tokens'] * model['input_price'] + r['output_tokens'] * model['output_price']) / 1_000_000 for r in records),
                projected_monthly_inr=monthly_cost(model['input_price'], model['output_price'],
                    {**budget, 'input_tokens_per_request': sum(r['input_tokens'] for r in records) / n,
                     'output_tokens_per_request': sum(r['output_tokens'] for r in records) / n}))
