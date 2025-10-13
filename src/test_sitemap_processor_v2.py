"""
Test pentru Darwin Sitemap Processor V2
"""

import unittest
from src.darwin_sitemap_processor_v2 import DarwinSitemapProcessor

class TestDarwinSitemapProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DarwinSitemapProcessor()
        
    def test_is_product_url(self):
        """Testează detecția URL-urilor de produse"""
        # URL-uri valide de produse
        valid_urls = [
            "https://darwin.md/telefoane/samsung-123",
            "https://darwin.md/laptopuri/lenovo-thinkpad-456",
            "https://darwin.md/accesorii/husa-789",
            "https://darwin.md/casti/airpods-234"
        ]
        
        for url in valid_urls:
            self.assertTrue(
                self.processor._is_product_url(url),
                f"URL-ul {url} ar trebui să fie detectat ca produs"
            )
            
        # URL-uri invalide
        invalid_urls = [
            "https://darwin.md/contact",
            "https://darwin.md/despre",
            "https://darwin.md/blog",
            "https://darwin.md/test.xml",
            "https://altsite.com/produs-123"
        ]
        
        for url in invalid_urls:
            self.assertFalse(
                self.processor._is_product_url(url),
                f"URL-ul {url} nu ar trebui să fie detectat ca produs"
            )
            
    def test_sitemap_parsing(self):
        """Testează parsarea conținutului sitemap"""
        test_content = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://darwin.md/telefoane/iphone-13</loc>
            </url>
            <url>
                <loc>https://darwin.md/laptopuri/macbook-air</loc>
            </url>
        </urlset>
        """
        
        urls = self.processor._parse_sitemap_content(test_content)
        self.assertEqual(len(urls), 2, "Ar trebui să găsească 2 URL-uri")
        self.assertIn("https://darwin.md/telefoane/iphone-13", urls)
        self.assertIn("https://darwin.md/laptopuri/macbook-air", urls)

if __name__ == '__main__':
    unittest.main()