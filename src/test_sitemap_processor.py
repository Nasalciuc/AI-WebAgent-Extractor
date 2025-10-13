#!/usr/bin/env python3
"""
Test script pentru procesorul optimizat de sitemap Darwin.md
"""

from darwin_sitemap_processor import DarwinSitemapProcessor
import json
import logging

def main():
    # Configurare logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Inițializare procesor
    processor = DarwinSitemapProcessor(
        max_workers=10,  # Număr de workers pentru procesare paralelă
        request_delay=0.5  # Delay între request-uri pentru a fi prietenos cu serverul
    )
    
    # Procesează sitemap-ul principal
    result = processor.process_sitemap_index("https://darwin.md/sitemap.xml")
    
    if result["success"]:
        print(f"\nProcesare completă cu succes!")
        print(f"Total URL-uri găsite: {result['total_urls']}")
        print(f"\nStatistici pe categorii:")
        for category, urls in result["categories"].items():
            print(f"- {category}: {len(urls)} produse")
            
        # Salvează rezultatele într-un fișier JSON
        output_file = "sitemap_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nRezultatele au fost salvate în: {output_file}")
    else:
        print(f"Eroare: {result.get('error', 'Eroare necunoscută')}")

if __name__ == "__main__":
    main()