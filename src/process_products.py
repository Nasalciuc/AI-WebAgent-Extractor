"""
Script pentru procesarea și analiza completă a produselor Darwin.md
"""

import json
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
import os

from darwin_sitemap_processor_v2 import DarwinSitemapProcessor
from darwin_product_analyzer import DarwinProductAnalyzer
from darwin_scraper_complete import DarwinProductScraper

class DarwinProductProcessor:
    """
    Procesor complet pentru produsele Darwin.md
    Combină sitemap parsing cu analiză detaliată
    """
    
    def __init__(self, output_dir: str = "data"):
        self.sitemap_processor = DarwinSitemapProcessor()
        self.product_analyzer = DarwinProductAnalyzer()
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        
        # Configurare logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configurează sistemul de logging"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/product_processing_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def process_single_product(self, url: str) -> Optional[Dict]:
        """
        Procesează un singur produs: descarcă pagina și extrage informații
        
        Args:
            url: URL-ul produsului
            
        Returns:
            Dict cu informațiile produsului sau None în caz de eroare
        """
        try:
            # Pauză pentru a nu supraîncărca serverul
            time.sleep(1)
            
            # Descarcă pagina
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            # Parsează HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrage titlul
            title = self._extract_title(soup)
            if not title:
                logging.warning(f"Nu s-a putut extrage titlul pentru {url}")
                return None
                
            # Analizează URL-ul și titlul
            attrs = self.product_analyzer.analyze_product_url(url)
            attrs = self.product_analyzer.analyze_product_title(title, attrs)
            
            # Extrage preț
            price_text = self._extract_price(soup)
            if price_text:
                price, currency = self.product_analyzer.analyze_price(price_text)
                attrs.price = price
                attrs.currency = currency
                
            # Extrage descriere
            description = self._extract_description(soup)
            
            # Extrage imagini
            images = self._extract_images(soup)
            
            # Extrage specificații adiționale
            specs = self._extract_specifications(soup)
            if specs:
                attrs.specs.update(specs)
                
            # Construiește rezultatul final
            result = {
                "url": url,
                "title": title,
                "description": description,
                "price": attrs.price,
                "currency": attrs.currency,
                "brand": attrs.brand,
                "model": attrs.model,
                "category": attrs.category,
                "subcategory": attrs.subcategory,
                "specs": attrs.specs,
                "images": images,
                "color": attrs.color,
                "capacity": attrs.capacity,
                "year": attrs.year,
                "extracted_at": datetime.now().isoformat()
            }
            
            logging.info(f"Produs procesat cu succes: {title}")
            return result
            
        except Exception as e:
            logging.error(f"Eroare la procesarea {url}: {str(e)}")
            return None
            
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrage titlul produsului"""
        selectors = [
            'h1.product-title',
            'h1[data-testid="product-title"]',
            'h1.title',
            'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
                
        return None
        
    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrage prețul produsului"""
        selectors = [
            '.price-current',
            '.price',
            '.product-price',
            '[data-testid="price"]',
            '.sale-price'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
                
        return None
        
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrage descrierea produsului"""
        selectors = [
            '.product-description',
            '.description',
            '[data-testid="description"]',
            '.product-details'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
                
        return ""
        
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extrage URL-urile imaginilor produsului"""
        images = []
        selectors = [
            '.product-gallery img',
            '.product-image img',
            '.gallery img'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for img in elements:
                src = img.get('src') or img.get('data-src')
                if src and not src.endswith('.svg'):
                    images.append(src)
                    
        return list(set(images))  # Elimină duplicate
        
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrage specificațiile tehnice ale produsului"""
        specs = {}
        spec_selectors = [
            '.specifications',
            '.product-specs',
            '.technical-details'
        ]
        
        for selector in spec_selectors:
            spec_table = soup.select_one(selector)
            if spec_table:
                # Încearcă să extragă din tabele sau liste
                rows = spec_table.select('tr') or spec_table.select('li')
                for row in rows:
                    # Pentru tabele
                    if row.select('th, td'):
                        key = row.select_one('th')
                        value = row.select_one('td')
                        if key and value:
                            specs[key.get_text().strip()] = value.get_text().strip()
                    # Pentru liste
                    else:
                        text = row.get_text().strip()
                        if ':' in text:
                            key, value = text.split(':', 1)
                            specs[key.strip()] = value.strip()
                            
        return specs
        
    def process_all_products(self, max_workers: int = 5, batch_size: int = 100) -> None:
        """
        Procesează toate produsele din sitemap
        
        Args:
            max_workers: Număr de thread-uri paralele
            batch_size: Mărime lot pentru salvare intermediară
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Crează directorul pentru output dacă nu există
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Procesează sitemap-ul
        logging.info("Începe procesarea sitemap-ului...")
        sitemap_results = self.sitemap_processor.process_sitemap("https://darwin.md/sitemap.xml")
        
        if not sitemap_results["success"]:
            logging.error("Eroare la procesarea sitemap-ului")
            return
            
        product_urls = sitemap_results["product_urls"]
        total_products = len(product_urls)
        logging.info(f"Găsite {total_products} URL-uri de produse")
        
        # Procesare produse în loturi
        processed_products = []
        current_batch = 1
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.process_single_product, url): url 
                      for url in product_urls}
            
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                    if result:
                        processed_products.append(result)
                        
                    # Salvează lot intermediar
                    if len(processed_products) % batch_size == 0:
                        self._save_batch(processed_products, timestamp, current_batch)
                        current_batch += 1
                        processed_products = []
                        
                except Exception as e:
                    logging.error(f"Eroare la procesarea {url}: {str(e)}")
                    
        # Salvează ultimul lot
        if processed_products:
            self._save_batch(processed_products, timestamp, current_batch)
            
        # Salvează statistici finale
        stats = {
            "total_urls": total_products,
            "processed_products": (current_batch - 1) * batch_size + len(processed_products),
            "processing_time": sitemap_results["stats"]["processing_time"],
            "completed_at": datetime.now().isoformat()
        }
        
        stats_file = os.path.join(self.output_dir, f'processing_stats_{timestamp}.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Procesare completă. Statistici salvate în {stats_file}")
        
    def _save_batch(self, products: List[Dict], timestamp: str, batch_number: int) -> None:
        """Salvează un lot de produse procesate"""
        # Salvează în JSON pentru backup
        json_filename = os.path.join(self.output_dir, 
                              f'products_batch_{batch_number}_{timestamp}.json')
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Salvat lotul {batch_number} cu {len(products)} produse în {json_filename}")
        
        # Exportă și în CSV folosind DarwinProductScraper
        scraper = DarwinProductScraper("dummy_key")  # cheia nu e necesară pentru export
        csv_filename = os.path.join(self.output_dir, f'products_batch_{batch_number}_{timestamp}.csv')
        scraper.export_to_csv(products, filename=csv_filename)
        logging.info(f"Exportat lotul {batch_number} în CSV: {csv_filename}")

def main():
    """Funcție principală pentru procesare"""
    processor = DarwinProductProcessor()
    processor.process_all_products()

if __name__ == "__main__":
    main()