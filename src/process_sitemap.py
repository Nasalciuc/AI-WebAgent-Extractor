"""
Script pentru procesarea sitemap-ului Darwin.md
"""

from darwin_sitemap_processor_v2 import DarwinSitemapProcessor
import json
from datetime import datetime

def main():
    # Inițializare procesor
    processor = DarwinSitemapProcessor()
    
    # Procesare sitemap
    print("Începem procesarea sitemap-ului...")
    results = processor.process_sitemap("https://darwin.md/sitemap.xml")
    
    if results["success"]:
        # Generare nume fișier cu timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"../data/sitemap_results_{timestamp}.json"
        
        # Export rezultate
        processor.export_results(output_file)
        print(f"Procesare completă. Rezultate salvate în {output_file}")
        print(f"Statistici:")
        print(f"- URL-uri totale: {results['stats']['total_urls']}")
        print(f"- URL-uri produse: {results['stats']['product_urls']}")
        print(f"- URL-uri eșuate: {results['stats']['failed_urls']}")
    else:
        print(f"Eroare: {results.get('error', 'Eroare necunoscută')}")

if __name__ == "__main__":
    main()