import json
from darwin_scraper_complete import DarwinProductScraper

s = object.__new__(DarwinProductScraper)
s.scraping_stats = {"urls_discovered":0, "products_extracted":0, "failed_extractions":0, "categories_found":0, "start_time":None, "end_time":None}
s.failed_urls = []
s.categories_found = set()

res = s.repair_jsonl_checkpoints("batch_local_1000.jsonl", "batch_local_1000_repaired")
print(json.dumps(res, ensure_ascii=False, indent=2))
