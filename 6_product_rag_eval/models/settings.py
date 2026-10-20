from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
DATA = PROJECT / 'docs/dataset'
GOLDENS = PROJECT / 'docs/goldends'
EMBEDDING_MODEL = 'nomic-ai/modernbert-embed-base'
COLLECTION = 'product_catalog_modernbert'
GENERATOR = 'openai/gpt-oss-120b'
JUDGE = 'gemini-3.5-flash-lite'
GENERATOR_INPUT_USD_M = 0.15
GENERATOR_OUTPUT_USD_M = 0.60
JUDGE_INPUT_USD_M = 0.30
JUDGE_OUTPUT_USD_M = 2.50
INR_PER_USD = 95  # Planning conversion; not live FX.
CANARY = 'RAG_EVAL_SYNTHETIC_CANARY_6'


def load_catalog():
    import json
    return json.loads((DATA / 'Hierarchical_Product_Catalog.json').read_text(encoding='utf-8-sig'))['products']
