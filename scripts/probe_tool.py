import sys, os
sys.path.insert(0, os.getcwd())
from darwin_scraper_complete import DarwinProductScraper
s = DarwinProductScraper(openai_api_key='test')
attr = getattr(s, 'discover_all_products')
print('instance attr type:', type(attr))
print('repr:', repr(attr))
try:
    import inspect
    print('inspect.signature on instance attr:')
    print(inspect.signature(attr))
except Exception as e:
    print('sig err:', e)
clsfunc = DarwinProductScraper.__dict__.get('discover_all_products')
print('class func type:', type(clsfunc))
print('class func repr:', repr(clsfunc))
try:
    print('inspect.signature class func:')
    import inspect
    print(inspect.signature(clsfunc))
except Exception as e:
    print('sig err2:', e)
