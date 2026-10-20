import json
import os
from time import perf_counter

import httpx
from dotenv import load_dotenv

from models.settings import GENERATOR, JUDGE, ROOT, GENERATOR_INPUT_USD_M, GENERATOR_OUTPUT_USD_M, JUDGE_INPUT_USD_M, JUDGE_OUTPUT_USD_M


def call_json(system, user, provider='groq'):
    load_dotenv(ROOT / '.env')
    started = perf_counter()
    if provider == 'groq':
        assert os.getenv('GROQ_API_KEY'), 'Set GROQ_API_KEY in the root .env.'
        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {'Authorization': 'Bearer ' + os.environ['GROQ_API_KEY']}
        payload = dict(model=GENERATOR, temperature=0, reasoning_effort='low', reasoning_format='hidden',
                       max_completion_tokens=1536, response_format={'type': 'json_object'},
                       messages=[dict(role='system', content=system), dict(role='user', content=user)])
    else:
        assert provider == 'gemini' and os.getenv('GOOGLE_API_KEY'), 'Set GOOGLE_API_KEY in the root .env.'
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{JUDGE}:generateContent'
        headers = {'x-goog-api-key': os.environ['GOOGLE_API_KEY']}
        payload = dict(systemInstruction={'parts': [{'text': system}]},
                       contents=[{'role': 'user', 'parts': [{'text': user}]}],
                       generationConfig={'temperature': 0, 'maxOutputTokens': 512,
                                         'responseMimeType': 'application/json', 'thinkingConfig': {'thinkingLevel': 'MINIMAL'}})
    response = httpx.post(url, headers=headers, json=payload, timeout=60)
    elapsed = perf_counter() - started
    if not response.is_success:
        return dict(ok=False, data=None, http_status=response.status_code,
                    error=response.json().get('error', {}).get('message', 'Provider request failed'),
                    seconds=elapsed, input_tokens=None, output_tokens=None, estimated_usd=None)
    body = response.json()
    if provider == 'groq':
        text = body['choices'][0]['message']['content']
        incoming, outgoing = body['usage']['prompt_tokens'], body['usage']['completion_tokens']
        input_price, output_price = GENERATOR_INPUT_USD_M, GENERATOR_OUTPUT_USD_M
    else:
        text = ''.join(p.get('text', '') for p in body['candidates'][0]['content']['parts'] if not p.get('thought'))
        usage = body['usageMetadata']
        incoming = usage['promptTokenCount']
        outgoing = usage.get('candidatesTokenCount', 0) + usage.get('thoughtsTokenCount', 0)
        input_price, output_price = JUDGE_INPUT_USD_M, JUDGE_OUTPUT_USD_M
    return dict(ok=True, data=json.loads(text), http_status=response.status_code, error=None,
                seconds=elapsed, input_tokens=incoming, output_tokens=outgoing,
                estimated_usd=(incoming * input_price + outgoing * output_price) / 1_000_000)
