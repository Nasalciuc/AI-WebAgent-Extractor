#!/usr/bin/env python3
"""Discover Darwin.md sitemap URLs and report counts and samples.

This script imports the project's DarwinProductScraper and runs only the
sitemap discovery step (no OpenAI calls, no product extraction). It prints
summary stats so you can confirm before extracting every product page.
"""
import sys
import os
import json

# Ensure project modules are importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from darwin_scraper_complete import DarwinProductScraper

# Import openai_config from the helper folder (AI-WebAgent-Extractor)
HELPER_DIR = os.path.join(ROOT, 'AI-WebAgent-Extractor')
if HELPER_DIR not in sys.path:
    sys.path.insert(0, HELPER_DIR)
try:
    import openai_config as oc
except Exception:
    oc = None


def main():
    # Try to get real OpenAI key if available (the scraper requires a key on init)
    # Prefer real key if the helper is available
    key = None
    if oc and hasattr(oc, 'get_openai_api_key'):
        try:
            key = oc.get_openai_api_key()
        except Exception:
            key = None
    if not key:
        key = "dummy"

    print("Using API key present:" , bool(key))

    scraper = DarwinProductScraper(openai_api_key=key)
    print("Instantiated DarwinProductScraper")

    print("Discovering sitemap URLs (this only parses sitemaps)...")

    # The method may be wrapped by the @tool decorator and not directly callable.
    discover_callable = getattr(scraper, 'discover_all_products', None)
    res = None
    if callable(discover_callable):
        try:
            res = discover_callable()
        except TypeError:
            # Maybe it's a bound method expecting no args but wrapper blocks call
            pass

    if res is None:
        # Try common wrapper attributes to reach the original function
        candidates = []
        if discover_callable is not None:
            for attr in ('__wrapped__', 'func', 'fn', 'function'):
                inner = getattr(discover_callable, attr, None)
                if inner:
                    candidates.append(inner)

        # Also try to get the raw function from the class dict
        raw = scraper.__class__.__dict__.get('discover_all_products')
        if raw:
            candidates.append(raw)

        # Try calling each candidate; prefer signatures that accept self
        from inspect import signature
        for cand in candidates:
            try:
                sig = signature(cand)
                params = len(sig.parameters)
                if params == 0:
                    res = cand()
                else:
                    res = cand(scraper)
                break
            except Exception:
                continue

    if res is None:
        raise RuntimeError('Could not invoke discover_all_products; wrapper unexpected')

    if not isinstance(res, dict):
        try:
            # Try to convert objects with attributes to dict
            res = dict(res)
        except Exception:
            res = {"success": False}

    print(json.dumps({
        "success": res.get("success", False),
        "sitemap_url": res.get("sitemap_url"),
        "total_urls_found": res.get("total_urls_found"),
        "product_count": res.get("product_count")
    }, indent=2, ensure_ascii=False))

    sample = res.get("product_urls", [])[:50]
    print(f"Sample product URLs (up to 50): {len(sample)}")
    for u in sample:
        print(u)

    print("Done. If you want to extract product pages, confirm and I will run the extractor.")


if __name__ == '__main__':
    main()
