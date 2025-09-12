import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI-WebAgent-Extractor'))
sys.path.insert(0, os.path.dirname(__file__))
from openai_config import get_openai_api_key as _gk
from darwin_scraper_complete import DarwinProductScraper
key=_gk()
s=DarwinProductScraper(key)
urls = [x['url'] if isinstance(x, dict) and 'url' in x else x for x in json.load(open('likely_products_strict.json', 'r', encoding='utf-8'))]
print('Using', len(urls), 'urls; running local batch on first 50')
res = s.run_batch_local_extraction(urls, workers=8, max_urls=50, output_prefix='batch_local_test', checkpoint_every=10)
print('Result:', res)
