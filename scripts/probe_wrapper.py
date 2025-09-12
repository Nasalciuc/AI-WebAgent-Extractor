import sys, os, inspect
sys.path.insert(0, os.getcwd())
from darwin_scraper_complete import DarwinProductScraper
s = DarwinProductScraper(openai_api_key='test')
a = getattr(s, 'discover_all_products')
print('instance attr type:', type(a))
print('callable:', callable(a))
print('repr:', repr(a))
for attr in ['__wrapped__','func','fn','function','f','__call__','__closure__','__qualname__']:
    val = getattr(a, attr, None)
    if val is not None:
        print(attr, '=>', type(val), repr(val)[:200])

print('---class dict entry---')
raw = DarwinProductScraper.__dict__.get('discover_all_products')
print('class dict entry type:', type(raw))
print('class dict repr:', repr(raw)[:400])
if hasattr(raw, '__wrapped__'):
    print('raw.__wrapped__ type', type(raw.__wrapped__))
print('done')
