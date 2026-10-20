"""Rerun one question with two retrieval settings and the same judge."""
import hashlib
import json
from datetime import datetime, timezone
from time import sleep

from models.settings import DATA, GOLDENS, PROJECT, GENERATOR, JUDGE, EMBEDDING_MODEL
from models.vector_store import load_vector_store
from services.rag import answer_question
from tools.quality_eval import judge_answer
from tools.retrieval_eval import load_cases


def run_example(question_id='Q61'):
    case = next(case for case in load_cases() if case['id'] == question_id)
    store = load_vector_store()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = PROJECT / 'docs/evalresults' / f'learning_{stamp}.json'
    experiment = dict(run_id=stamp, question_id=question_id, question=case['question'],
                      expected_answer=case['expected_answer'], human_review='pending',
                      generator=GENERATOR, judge=JUDGE, embedding_model=EMBEDDING_MODEL, k=1,
                      catalog_sha256=hashlib.sha256((DATA / 'Hierarchical_Product_Catalog.json').read_bytes()).hexdigest(),
                      goldens_sha256=hashlib.sha256((GOLDENS / 'retrieval_cases.json').read_bytes()).hexdigest(),
                      versions={})
    for version, mode in [('baseline', 'semantic'), ('candidate', 'catalog')]:
        answer = answer_question(store, case['question'], k=1, mode=mode)
        assert answer['provider']['ok'], answer['provider']['error']
        judgment = judge_answer(case, answer)
        assert judgment['ok'], judgment.get('error')
        experiment['versions'][version] = dict(mode=mode, answer=answer, judgment=judgment)
        destination.write_text(json.dumps(experiment, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(version, '| completeness:', judgment['data']['completeness'], flush=True)
        if version == 'baseline':
            sleep(8)  # Space the two generation requests on the existing provider plan.
    print('Saved:', destination)
    return experiment


if __name__ == '__main__':
    run_example()
