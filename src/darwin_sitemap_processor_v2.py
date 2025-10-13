"""
Darwin.md Sitemap Processor V2 - Versiune simplificată și robustă
"""

import requests
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import re
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
import json

class DarwinSitemapProcessor:
    """Procesor specializat pentru sitemap-ul Darwin.md"""
    
    def __init__(self, base_url: str = "https://darwin.md"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.product_urls: Set[str] = set()
        self.failed_urls: List[str] = []
        self.stats = {
            "total_urls": 0,
            "product_urls": 0,
            "failed_urls": 0,
            "processing_time": 0
        }

    def _fetch_sitemap(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Descarcă conținutul sitemap-ului cu reîncercări"""
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=self.headers, timeout=20)
                resp.raise_for_status()
                return resp.content.decode('utf-8')
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to fetch sitemap {url}: {str(e)}")
                    return None
                time.sleep(2 ** attempt)  # exponential backoff
        return None

    def _parse_sitemap_content(self, content: str) -> List[str]:
        """Extrage toate URL-urile dintr-un sitemap XML"""
        urls: List[str] = []
        try:
            root = ET.fromstring(content)
            # Namespace pentru sitemap
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Încearcă să extragă din sitemap index
            for sitemap in root.findall('.//ns:sitemap/ns:loc', ns):
                if sitemap.text:
                    urls.append(sitemap.text.strip())
            
            # Încearcă să extragă URL-uri directe
            for url in root.findall('.//ns:url/ns:loc', ns):
                if url.text:
                    urls.append(url.text.strip())
                    
        except Exception as e:
            logging.error(f"Error parsing sitemap content: {str(e)}")
            
        return urls

    def _is_product_url(self, url: str) -> bool:
        """
        Verifică dacă un URL este o pagină de produs, folosind reguli simplificate
        """
        if not url.startswith(self.base_url):
            return False

        # Șabloane de URL-uri pentru produse
        product_patterns = [
            r'/telefoane/',
            r'/laptopuri/',
            r'/tablete/',
            r'/accesorii/',
            r'/audio/',
            r'/gaming/',
            r'/smart-home/',
            r'/electronice/',
            r'/monitoare/',
            r'/smartphone/',
            r'/casti/',
            r'/boxe/'
        ]

        # URL-uri de exclus
        exclude_patterns = [
            r'/contact',
            r'/despre',
            r'/cos',
            r'/login',
            r'/blog',
            r'/ajutor',
            r'/termeni',
            r'.xml$',
            r'.pdf$',
            r'.jpg$'
        ]

        # Verifică excluderile
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.I):
                return False

        # Verifică modelele de produs
        has_product_pattern = any(re.search(pattern, url, re.I) for pattern in product_patterns)

        # Verifică ID-ul produsului
        has_id = bool(re.search(r'/\d+/?$', url)) or bool(re.search(r'-\d+/?$', url))

        # Trebuie să aibă cel puțin un pattern de produs SAU un ID
        return has_product_pattern or has_id

    def process_urls(self, urls: List[str], max_workers: int = 10) -> None:
        """Procesează URL-urile folosind ThreadPoolExecutor"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self._process_single_url, urls)
            
            for result in results:
                if result and isinstance(result, list):
                    for url in result:
                        if self._is_product_url(url):
                            self.product_urls.add(url)
                        self.stats["total_urls"] += 1

    def _process_single_url(self, url: str) -> Optional[List[str]]:
        """Procesează un singur URL de sitemap"""
        try:
            content = self._fetch_sitemap(url)
            if not content:
                self.failed_urls.append(url)
                self.stats["failed_urls"] += 1
                return None
                
            urls = self._parse_sitemap_content(content)
            return urls
            
        except Exception as e:
            logging.error(f"Error processing URL {url}: {str(e)}")
            self.failed_urls.append(url)
            self.stats["failed_urls"] += 1
            return None

    def process_sitemap(self, sitemap_url: str) -> Dict:
        """
        Procesează sitemap-ul principal și toate subsitemap-urile
        """
        start_time = time.time()
        
        # Descarcă sitemap-ul principal
        content = self._fetch_sitemap(sitemap_url)
        if not content:
            return {
                "success": False,
                "error": "Could not fetch main sitemap",
                "stats": self.stats
            }

        # Extrage URL-urile inițiale
        initial_urls = self._parse_sitemap_content(content)
        if not initial_urls:
            return {
                "success": False,
                "error": "No URLs found in main sitemap",
                "stats": self.stats
            }

        # Procesează URL-urile în paralel
        self.process_urls(initial_urls)
        
        # Actualizează statisticile
        self.stats["processing_time"] = time.time() - start_time
        self.stats["product_urls"] = len(self.product_urls)
        
        return {
            "success": True,
            "product_urls": list(self.product_urls),
            "failed_urls": self.failed_urls,
            "stats": self.stats
        }

    def export_results(self, output_file: str) -> None:
        """Exportă rezultatele într-un fișier JSON"""
        results = {
            "product_urls": list(self.product_urls),
            "failed_urls": self.failed_urls,
            "stats": self.stats
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)