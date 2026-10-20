import json


from models.llm import call_json
from models.settings import PROJECT


SCORES = ['correctness', 'completeness', 'faithfulness', 'answer_relevance',
          'context_relevance', 'style', 'order', 'toxicity', 'scope_adherence']


def judge_answer(case, record):
    if not record['provider']['ok']:
        return dict(id=case['id'], ok=False, error='Generation failed; no quality score assigned.')
    system = (PROJECT / 'prompts/judge.md').read_text(encoding='utf-8')
    user = json.dumps(dict(question=case['question'], expected_answer=case['expected_answer'],
                           actual_answer=record['answer'], context=record['context'],
                           catalog_complete=record['catalog_complete']), ensure_ascii=False)
    response = call_json(system, user, provider='gemini')
    if response['ok']:
        assert all(isinstance(response['data'][key], (int, float)) and 0 <= response['data'][key] <= 1 for key in SCORES)
    return dict(id=case['id'], **response)
