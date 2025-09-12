#!/usr/bin/env python3
"""Run DarwinProductScraper sitemap discovery by invoking the class function
directly to avoid the @tool wrapper. Prints totals and a sample of product URLs.
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure helper folder on path
HELPER_DIR = os.path.join(ROOT, 'AI-WebAgent-Extractor')
if HELPER_DIR not in sys.path:
    sys.path.insert(0, HELPER_DIR)

# Import modules
from darwin_scraper_complete import DarwinProductScraper
try:
    import openai_config as oc
except Exception:
    oc = None

# Get key if available
key = None
if oc and hasattr(oc, 'get_openai_api_key'):
    try:
        key = oc.get_openai_api_key()
    except Exception:
        key = None
if not key:
    key = 'dummy'

print('Using API key present:', bool(key) and key != 'dummy')

scraper = DarwinProductScraper(openai_api_key=key)
print('Instantiated DarwinProductScraper')

# Obtain the tool-wrapped attribute from the instance and call its entrypoint
discover_attr = getattr(scraper, 'discover_all_products', None)
if discover_attr is None:
    raise SystemExit('discover_all_products not found on instance')

print('Invoking discover_all_products via wrapper entrypoint')
res = None
if hasattr(discover_attr, 'entrypoint') and callable(getattr(discover_attr, 'entrypoint')):
    # entrypoint is the original function (unbound)
    try:
        res = discover_attr.entrypoint(scraper, 'https://darwin.md/sitemap.xml')
    except TypeError:
        # maybe the entrypoint expects only self
        res = discover_attr.entrypoint(scraper)
elif callable(discover_attr):
    try:
        res = discover_attr()
    except Exception as e:
        res = None

if res is None:
    raise SystemExit('Failed to get discovery result')

if not isinstance(res, dict):
    try:
        res = dict(res)
    except Exception:
        res = {'success': False}

print(json.dumps({
    'success': res.get('success', False),
    'sitemap_url': res.get('sitemap_url'),
    'total_urls_found': res.get('total_urls_found'),
    'product_count': res.get('product_count')
}, indent=2, ensure_ascii=False))

sample = res.get('product_urls', [])[:50]
print('\nSample product URLs (up to 50):', len(sample))
for u in sample:
    print(u)

print('\nDone')
