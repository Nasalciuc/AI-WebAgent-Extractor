# QA sample script: sample URLs, fetch HTML+heuristics, and ask OpenAI for an analysis
import sys
import os
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI-WebAgent-Extractor'))
sys.path.insert(0, os.path.dirname(__file__))

from openai_config import get_openai_api_key
from darwin_scraper_complete import DarwinProductScraper

import requests
from bs4 import BeautifulSoup

OUT_JSON = 'diagnostics_sample_100.json'
OUT_SUMMARY = 'diagnostics_ai_summary.txt'

KEY = get_openai_api_key()
print('OpenAI key present' if KEY else 'No OpenAI key found')

scraper = DarwinProductScraper(KEY)

# load likely list
with open('likely_products_strict.json', 'r', encoding='utf-8') as f:
    likely = json.load(f)
urls = [item['url'] if isinstance(item, dict) and 'url' in item else item for item in likely]
print('Total likely URLs:', len(urls))

SAMPLE_N = min(100, len(urls))
sample = random.sample(urls, SAMPLE_N)

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (compatible; QA-bot/1.0)'}

def analyze_url(url):
    out = {'url': url}
    try:
        r = session.get(url, headers=headers, timeout=12)
        out['status_code'] = r.status_code
        text = r.text or ''
        out['length'] = len(text)
        out['snippet'] = text[:1000]
        # quick heuristics from the scraper
        try:
            quick = scraper._quick_is_product_page(url, html=text)
        except Exception as e:
            quick = {'url': url, 'is_product': False, 'score': 0.0, 'reasons': [f'quick_error:{e}']}
        out['quick'] = quick
        try:
            specs = scraper._extract_spec_features(text)
        except Exception as e:
            specs = {'found': [], 'count': 0, 'error': str(e)}
        out['specs'] = specs
        # find JSON-LD product presence
        soup = BeautifulSoup(text, 'html.parser')
        ld = []
        for s in soup.find_all('script', type='application/ld+json'):
            try:
                ldj = json.loads(s.string or '{}')
            except Exception:
                # try to be forgiving
                try:
                    ldj = json.loads((s.string or '').strip())
                except Exception:
                    ldj = None
            ld.append(ldj)
        out['jsonld_count'] = len(ld)
        out['jsonld_product'] = any(isinstance(j, dict) and j.get('@type') in ('Product', 'Offer') or (isinstance(j, list) and any(x.get('@type') in ('Product','Offer') for x in j if isinstance(x, dict))) for j in ld)
        # meta title and h1
        out['title'] = (soup.title.string.strip() if soup.title and soup.title.string else '')
        h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
        out['h1_count'] = len(h1s)
        out['h1'] = h1s[:3]
    except Exception as e:
        out['error'] = str(e)
    return out

print('Fetching and analyzing sample of', SAMPLE_N)
results = []
with ThreadPoolExecutor(max_workers=12) as ex:
    futures = {ex.submit(analyze_url, u): u for u in sample}
    for i, fut in enumerate(as_completed(futures)):
        try:
            r = fut.result()
        except Exception as e:
            r = {'url': futures[fut], 'error': str(e)}
        results.append(r)
        if (i+1) % 10 == 0:
            print('Processed', i+1, 'of', SAMPLE_N)

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump({'sample_n': SAMPLE_N, 'timestamp': time.time(), 'results': results}, f, ensure_ascii=False, indent=2)

# Try to call OpenAI to summarize
prompt = "Analyze the following diagnostics for why product pages may be mis-identified. Provide top 6 failure patterns with examples and actionable fixes. Return plain text.\n\nDiagnostics JSON summary:\n"
# create an aggregated summary for the prompt to keep token size manageable
agg = {'total': SAMPLE_N, 'jsonld_products': 0, 'avg_length': 0, 'quick_scores': [], 'reasons_count': {}}
lengths = []
for r in results:
    lengths.append(r.get('length', 0))
    if r.get('jsonld_product'):
        agg['jsonld_products'] += 1
    qs = r.get('quick', {})
    agg['quick_scores'].append(qs.get('score', 0.0))
    for reason in qs.get('reasons', []):
        agg['reasons_count'][reason] = agg['reasons_count'].get(reason, 0) + 1

agg['avg_length'] = sum(lengths)/len(lengths) if lengths else 0
# pick 6 examples: 3 jsonld true, 3 jsonld false but high score
examples = []
for r in results:
    if r.get('jsonld_product') and len(examples) < 3:
        examples.append({'url': r['url'], 'title': r.get('title',''), 'jsonld': True, 'quick': r.get('quick',{})})
for r in sorted(results, key=lambda x: -x.get('quick',{}).get('score',0)):
    if len(examples) >= 6:
        break
    if not r.get('jsonld_product'):
        examples.append({'url': r['url'], 'title': r.get('title',''), 'jsonld': False, 'quick': r.get('quick',{})})

prompt += json.dumps({'agg': agg, 'examples': examples}, ensure_ascii=False, indent=2)

summary_text = ''
try:
    import openai
    openai.api_key = KEY
    model = 'gpt-3.5-turbo'
    print('Calling OpenAI for summary...')
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{'role':'user','content': prompt}],
        temperature=0.0,
        max_tokens=600
    )
    summary_text = resp['choices'][0]['message']['content'].strip()
except Exception as e:
    print('OpenAI call failed or not available:', e)
    # fallback: create a local summary
    reasons = sorted(agg['reasons_count'].items(), key=lambda x:-x[1])
    summary_lines = [f"Sample size: {SAMPLE_N}", f"JSON-LD products: {agg['jsonld_products']}", f"Avg page length: {agg['avg_length']:.1f}", "Top quick reasons:"]
    for k,c in reasons[:10]:
        summary_lines.append(f" - {k}: {c}")
    summary_lines.append('\nExamples:')
    for ex in examples:
        summary_lines.append(f" - {ex['url']} title={ex['title'][:80]} jsonld={ex['jsonld']} score={ex['quick'].get('score')}")
    summary_text = '\n'.join(summary_lines)

with open(OUT_SUMMARY, 'w', encoding='utf-8') as f:
    f.write(summary_text)

print('Wrote', OUT_JSON, 'and', OUT_SUMMARY)
print('Done')
