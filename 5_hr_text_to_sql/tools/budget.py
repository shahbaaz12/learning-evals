"""Six.md: reject over-budget models, then weight coding quality and speed."""
import json

from models.settings import DATA, PROJECT


def monthly_cost(input_price, output_price, budget):
    per_request = (budget['input_tokens_per_request'] * input_price
                   + budget['output_tokens_per_request'] * output_price) / 1_000_000
    return per_request * budget['requests_per_day'] * budget['days_per_month'] * budget['inr_per_usd'] * (1 + budget['contingency_fraction'])


def shortlist():
    budget = json.loads((DATA / 'budget.json').read_text(encoding='utf-8'))
    snapshot = json.loads((DATA / 'llm_stats_snapshot.json').read_text(encoding='utf-8'))
    eligible = []
    rejected = []
    for source in snapshot['models']:
        row = dict(source)
        if any(row.get(key) is None for key in ['input_price', 'output_price', 'index_code']):
            continue
        row['monthly_inr'] = round(monthly_cost(row['input_price'], row['output_price'], budget), 2)
        (eligible if row['monthly_inr'] <= budget['monthly_budget_inr'] else rejected).append(row)
    qualities = [r['index_code'] for r in eligible]
    speeds = [r['throughput'] for r in eligible if r.get('throughput') is not None]
    assert len(eligible) >= 4 and speeds, 'Need four affordable models and at least one measured speed.'
    for row in eligible:
        row['quality_normalized'] = (row['index_code'] - min(qualities)) / (max(qualities) - min(qualities)) if max(qualities) != min(qualities) else 1.0
        row['speed_missing'] = row.get('throughput') is None
        row['speed_normalized'] = 0.5 if row['speed_missing'] or max(speeds) == min(speeds) else (row['throughput'] - min(speeds)) / (max(speeds) - min(speeds))
        row['selection_score'] = budget['quality_weight'] * row['quality_normalized'] + budget['speed_weight'] * row['speed_normalized']
    eligible.sort(key=lambda r: (-r['selection_score'], r['monthly_inr'], r['model_id']))
    return dict(budget=budget, snapshot_fetched_at=snapshot['fetched_at'],
                shortlisted=eligible[:4], eligible=eligible, rejected_over_budget=rejected,
                quality_only_top_four=[r['model_id'] for r in sorted(eligible, key=lambda r: -r['index_code'])[:4]],
                method='Min-max coding index and source throughput (characters/second) over eligible models; missing speed = neutral 0.5. Higher speed is better. Source speed is not application latency.',
                status='Planning shortlist only; custom model evaluation pending.')


def save_shortlist():
    report = shortlist()
    path = PROJECT / 'docs' / 'evalresults' / 'model_shortlist.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for row in report['shortlisted']:
        print(row['name'], row['input_price'], row['output_price'], row['monthly_inr'], round(row['selection_score'], 4))
    return report
