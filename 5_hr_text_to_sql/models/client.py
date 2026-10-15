"""Small provider-specific requests. No framework, retries, or hidden model calls."""
import os
import httpx

from dotenv import load_dotenv

from models.candidates import load_selection
from models.settings import DATA, PROJECT, ROOT


def build_prompt(question):
    system = (PROJECT / 'prompts/text_to_sql.md').read_text(encoding='utf-8')
    user = ('Schema:\n' + (DATA / 'schema.sql').read_text(encoding='utf-8')
            + '\nBusiness rules:\n' + (DATA / 'business_rules.md').read_text(encoding='utf-8')
            + '\nHR question:\n' + question)
    return system, user


def call_model(model_id, question):
    load_dotenv(ROOT / '.env')
    model = next(m for m in load_selection()['shortlisted'] if m['model_id'] == model_id)
    key_name, api_model = model['key_name'], model['model_id']
    assert os.getenv(key_name), f'Add {key_name} to the repository root .env.'
    key = os.environ[key_name]
    system, user = build_prompt(question)
    headers = {'Content-Type': 'application/json'}
    if model['provider'] == 'gemini':
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent'
        headers['x-goog-api-key'] = key
        payload = dict(systemInstruction={'parts': [{'text': system}]},
                       contents=[{'role': 'user', 'parts': [{'text': user}]}],
                       generationConfig={'maxOutputTokens': model['max_output_tokens'],
                                         'thinkingConfig': model['thinking_config']})
    else:
        assert model['provider'] == 'groq'
        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers['Authorization'] = f'Bearer {key}'
        payload = dict(model=api_model, max_completion_tokens=model['max_output_tokens'],
                       reasoning_effort=model['reasoning_effort'], reasoning_format='hidden', temperature=0,
                       messages=[dict(role='system', content=system), dict(role='user', content=user)])
    response = httpx.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    if model['provider'] == 'gemini':
        candidate = data['candidates'][0]
        sql = '\n'.join(part['text'] for part in candidate['content']['parts'] if 'text' in part and not part.get('thought'))
        usage = data['usageMetadata']
        incoming = usage['promptTokenCount']
        outgoing = usage.get('candidatesTokenCount', 0) + usage.get('thoughtsTokenCount', 0)
        finish = candidate.get('finishReason')
    else:
        sql = data['choices'][0]['message']['content'] or ''
        incoming, outgoing = data['usage']['prompt_tokens'], data['usage']['completion_tokens']
        finish = data['choices'][0]['finish_reason']
    sql = sql.strip()
    if sql.startswith('```') and sql.endswith('```'):
        sql = '\n'.join(sql.splitlines()[1:-1]).strip()
    return dict(sql=sql, input_tokens=incoming, output_tokens=outgoing,
                api_model=api_model, provider=model['provider'],
                reasoning_effort=model['reasoning_effort'], finish_reason=finish)
