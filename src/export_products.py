#!/usr/bin/env python3
"""
Script pentru exportul produselor Darwin.md în CSV
Folosește funcționalitatea completă din DarwinScraper
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from darwin_scraper_complete import DarwinProductScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export.log'),
        logging.StreamHandler()
    ]
)

def load_batch_products(data_dir: str = "data") -> List[Dict[str, Any]]:
    """Încarcă toate produsele din fișierele batch JSON"""
    all_products = []
    
    # Găsește toate fișierele batch
    batch_files = [f for f in os.listdir(data_dir) if f.startswith("products_batch_") and f.endswith(".json")]
    
    for batch_file in batch_files:
        try:
            with open(os.path.join(data_dir, batch_file), 'r', encoding='utf-8') as f:
                products = json.load(f)
                all_products.extend(products)
            logging.info(f"Încărcat {len(products)} produse din {batch_file}")
        except Exception as e:
            logging.error(f"Eroare la încărcarea {batch_file}: {e}")
    
    return all_products

def main():
    """Funcția principală"""
    logging.info("Începe exportul produselor")
    
    # Inițializează scraper-ul (doar pentru funcțiile de export)
    scraper = DarwinProductScraper("dummy_key") # cheia nu e necesară pentru export
    
    try:
        # Încarcă toate produsele din fișierele batch
        all_products = load_batch_products()
        logging.info(f"Încărcate {len(all_products)} produse în total")
        
        # Exportă în CSV folosind funcția specializată din scraper
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"data/all_products_{timestamp}.csv"
        
        csv_path = scraper.export_to_csv(all_products, filename=csv_file)
        logging.info(f"Date exportate cu succes în: {csv_path}")
        
        # Statistici
        valid_products = [p for p in all_products if p.get("is_valid")]
        logging.info(f"Produse valide: {len(valid_products)} din {len(all_products)}")
        
        # Listează categoriile unice
        categories = set(p.get("category", "Necunoscut") for p in all_products)
        logging.info(f"Categorii găsite: {len(categories)}")
        for cat in sorted(categories):
            count = sum(1 for p in all_products if p.get("category") == cat)
            logging.info(f"- {cat}: {count} produse")
            
    except Exception as e:
        logging.error(f"Eroare la export: {e}")
        raise

if __name__ == "__main__":
    main()