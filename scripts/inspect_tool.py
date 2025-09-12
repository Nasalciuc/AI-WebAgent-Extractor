import sys, os
sys.path.insert(0, os.getcwd())
from darwin_scraper_complete import DarwinProductScraper
s = DarwinProductScraper(openai_api_key='test')
inst_attr = getattr(s, 'discover_all_products')
cls_attr = DarwinProductScraper.__dict__.get('discover_all_products')
print('INSTANCE ATTR TYPE:', type(inst_attr))
print('INSTANCE ATTR DIR:', [a for a in dir(inst_attr) if not a.startswith('_')])
print('INSTANCE ATTR REPR:', repr(inst_attr))
print('\nCLASS ATTR TYPE:', type(cls_attr))
print('CLASS ATTR DIR:', [a for a in dir(cls_attr) if not a.startswith('_')])
print('CLASS ATTR REPR:', repr(cls_attr))
# Try common wrapper attributes
for name in ('__wrapped__','function','fn','func','callable','__call__'):
    if hasattr(inst_attr, name):
        print('inst has', name, '->', getattr(inst_attr, name))
    if hasattr(cls_attr, name):
        print('cls has', name, '->', getattr(cls_attr, name))
# Try calling with introspection
import inspect
for objname,obj in (('inst_attr',inst_attr),('cls_attr',cls_attr)):
    print('\nInspect',objname)
    try:
        print('callable:', callable(obj))
    except Exception as e:
        print('callable err', e)
    try:
        print('signature:', inspect.signature(obj))
    except Exception as e:
        print('signature err', e)

print('\nDone')
