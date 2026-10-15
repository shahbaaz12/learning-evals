"""Explicit network preparation step. Freeze the public LLM Stats model table."""
import json
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from models.settings import DATA
from tools.budget import save_shortlist


URL = 'https://llm-stats.com/leaderboards/llm-leaderboard'
# Correct conditional/provider-specific prices before calculating the budget.
OVERRIDES = {
    'deepseek-v4.1-flash': (0.30, 1.20, 'Native DeepSeek, uncached peak rates; https://api-docs.deepseek.com/quick_start/pricing'),
    'mistral-large-4': (1.36, 4.18, 'Standard Mistral rates, excluding preview promotion; https://docs.mistral.ai/models/mistral-large'),
    'muse-spark-1.3': (1.25, 4.25, 'Standard rates, excluding contributor discount; https://llm-stats.com/models/muse-spark-1.3'),
}


def refresh():
    with urlopen(Request(URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as response:
        html = response.read().decode('utf-8')
    parts = []
    for match in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>', html):
        item = json.loads(match.group(1))
        if len(item) > 1 and isinstance(item[1], str):
            parts.append(item[1])
    payload = ''.join(parts)
    decoder = json.JSONDecoder()
    models = {}
    for match in re.finditer(r'\{"model_id":', payload):
        source, _ = decoder.raw_decode(payload, match.start())
        row = {key: source.get(key) for key in ['model_id', 'name', 'organization',
               'input_price', 'output_price', 'index_code', 'throughput', 'latency']}
        row['price_basis'] = f"LLM Stats model table: https://llm-stats.com/models/{row['model_id']}"
        if row['model_id'] in OVERRIDES:
            row['site_input_price'] = row['input_price']
            row['site_output_price'] = row['output_price']
            row['input_price'], row['output_price'], row['price_basis'] = OVERRIDES[row['model_id']]
        models[row['model_id']] = row
    assert len(models) > 50, 'Source layout changed; preserve the existing snapshot and inspect the page.'
    document = dict(source_url=URL, fetched_at=datetime.now(timezone.utc).isoformat(),
                    prices_unit='USD per million tokens', models=list(models.values()))
    (DATA / 'llm_stats_snapshot.json').write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
    print(f'Frozen {len(models)} models from LLM Stats.')
    save_shortlist()


if __name__ == '__main__':
    refresh()
