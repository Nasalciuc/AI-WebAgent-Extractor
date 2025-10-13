"""
Darwin.md Sitemap Processor - Optimizat pentru procesare paralelă
"""
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET
import requests
from urllib.parse import urljoin, urlparse

class DarwinSitemapProcessor:
    """Procesor optimizat pentru sitemap-urile Darwin.md"""
    
    def __init__(self, base_url: str = "https://darwin.md",
                 max_workers: int = 10,
                 request_delay: float = 0.5):
        self.base_url = base_url
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.processed_urls: Set[str] = set()
        self.category_patterns = self._build_category_patterns()
        
        # Configurare logging
        self.logger = logging.getLogger('darwin_sitemap')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def _build_category_patterns(self) -> Dict[str, List[str]]:
        """Construiește patterns pentru categorii bazate pe URL-uri"""
        return {
            'Telefoane': [r'/smartphone', r'/telefoane-mobile', r'/phone'],
            'Laptopuri': [r'/laptop', r'/notebook'],
            'Tablete': [r'/tablet', r'/ipad'],
            'Audio': [r'/casti', r'/boxe', r'/audio'],
            'Gaming': [r'/gaming', r'/console', r'/jocuri'],
            'Accesorii': [r'/accesorii', r'/accessory'],
            'TV': [r'/televizoare', r'/tv'],
            'Computere': [r'/pc', r'/computer', r'/sisteme'],
            'Componente': [r'/componente', r'/piese'],
            'Smart Home': [r'/smart-home', r'/casa-inteligenta'],
        }

    def process_sitemap_index(self, sitemap_url: str) -> Dict[str, any]:
        """Procesează sitemap index și toate subsitemaps în paralel"""
        self.logger.info(f"Începe procesarea sitemap index: {sitemap_url}")
        
        try:
            # Descarcă sitemap index
            content = self._fetch_url(sitemap_url)
            if not content:
                return {"success": False, "error": "Nu s-a putut descărca sitemap index"}

            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Extrage toate subsitemaps
            sitemaps = []
            for sitemap in root.findall('.//ns:sitemap/ns:loc', namespace):
                if sitemap.text:
                    sitemaps.append(sitemap.text.strip())

            self.logger.info(f"Găsite {len(sitemaps)} subsitemaps")
            
            # Procesează subsitemaps în paralel
            all_urls = []
            categories = {}
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {
                    executor.submit(self._process_subsitemap, url): url 
                    for url in sitemaps
                }
                
                for future in as_completed(future_to_url):
                    sitemap_url = future_to_url[future]
                    try:
                        result = future.result()
                        if result.get("success"):
                            all_urls.extend(result.get("urls", []))
                            # Actualizează categoriile
                            cat = result.get("category", "")
                            if cat:
                                if cat not in categories:
                                    categories[cat] = []
                                categories[cat].extend(result.get("urls", []))
                    except Exception as e:
                        self.logger.error(f"Eroare la procesarea {sitemap_url}: {str(e)}")
                        continue

            # Deduplică URL-urile păstrând ordinea
            unique_urls = []
            seen = set()
            for url in all_urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            return {
                "success": True,
                "total_urls": len(unique_urls),
                "urls": unique_urls,
                "categories": categories,
                "stats": {
                    "total_sitemaps": len(sitemaps),
                    "categories_found": len(categories)
                }
            }

        except Exception as e:
            self.logger.error(f"Eroare la procesarea sitemap index: {str(e)}")
            return {"success": False, "error": str(e)}

    def _process_subsitemap(self, sitemap_url: str) -> Dict[str, any]:
        """Procesează un subsitemap individual și extrage URL-urile de produse"""
        try:
            # Extrage categoria din URL
            category = self._extract_category_from_url(sitemap_url)
            
            content = self._fetch_url(sitemap_url)
            if not content:
                return {"success": False, "error": "Nu s-a putut descărca subsitemap"}

            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            urls = []
            for url_elem in root.findall('.//ns:url/ns:loc', namespace):
                if url_elem.text:
                    url = url_elem.text.strip()
                    if self._is_product_url(url):
                        urls.append(url)

            return {
                "success": True,
                "category": category,
                "urls": urls,
                "count": len(urls)
            }

        except Exception as e:
            self.logger.error(f"Eroare la procesarea subsitemap {sitemap_url}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _fetch_url(self, url: str) -> Optional[str]:
        """Descarcă conținutul unui URL cu rate limiting și retry"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xml;q=0.9,*/*;q=0.8'
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(self.request_delay)  # Rate limiting
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.content
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Eroare finală la descărcarea {url}: {str(e)}")
                    return None
                self.logger.warning(f"Încercare {attempt + 1} eșuată pentru {url}: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None

    def _is_product_url(self, url: str) -> bool:
        """Verifică dacă un URL este pentru o pagină de produs"""
        if not url or not url.startswith(self.base_url):
            return False

        # Exclude URL-uri non-produs evidente
        exclude_patterns = [
            r'/contact', r'/about', r'/cart', r'/checkout',
            r'/login', r'/register', r'/blog', r'/news',
            r'\.xml$', r'\.css$', r'\.js$', r'\.jpg$', r'\.png$'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.I):
                return False

        # Verifică modelele de URL pentru produse
        product_patterns = [
            r'/p/[a-z0-9-]+$',  # URL-uri de produs standard
            r'/product/[a-z0-9-]+$',  # URL-uri alternative de produs
            r'/[a-z-]+/[a-z0-9-]+-\d+$',  # URL-uri cu ID numeric la sfârșit
            r'/[^/]+/[^/]+/[^/]+$'  # URL-uri cu 3 nivele (categorie/subcategorie/produs)
        ]
        
        return any(re.search(pattern, url, re.I) for pattern in product_patterns)

    def _extract_category_from_url(self, url: str) -> str:
        """Extrage categoria din URL-ul sitemap"""
        try:
            # Extrage numele fișierului din URL
            filename = url.split('/')[-1].replace('.xml', '')
            
            # Extrage numele categoriei (elimină ID-ul numeric)
            category_name = re.sub(r'-\d+$', '', filename)
            
            # Curăță și formatează numele categoriei
            category_name = category_name.replace('-', ' ').title()
            
            return category_name
        except Exception:
            return "General"

    def get_category_for_url(self, url: str) -> str:
        """Determină categoria pentru un URL de produs"""
        url_lower = url.lower()
        
        for category, patterns in self.category_patterns.items():
            if any(re.search(pattern, url_lower) for pattern in patterns):
                return category
                
        return "General"