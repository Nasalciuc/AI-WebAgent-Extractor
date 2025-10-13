"""
Teste pentru analizorul de produse Darwin
"""

import unittest
from darwin_product_analyzer import DarwinProductAnalyzer, ProductAttributes

class TestDarwinProductAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DarwinProductAnalyzer()
        
    def test_analyze_smartphone_url(self):
        """Test pentru analiza URL-urilor de smartphone"""
        urls = [
            ("https://darwin.md/telefoane/samsung-galaxy-s21-ultra-5g-128gb-black", {
                "brand": "samsung",
                "model": "s21",
                "category": "smartphones",
                "subcategory": "flagship"
            }),
            ("https://darwin.md/telefoane/apple-iphone-13-pro-max-256gb-silver", {
                "brand": "apple",
                "model": "13 pro max",
                "category": "smartphones",
                "subcategory": "flagship"
            })
        ]
        
        for url, expected in urls:
            attrs = self.analyzer.analyze_product_url(url)
            self.assertEqual(attrs.brand, expected["brand"])
            self.assertEqual(attrs.category, expected["category"])
            
    def test_analyze_laptop_url(self):
        """Test pentru analiza URL-urilor de laptop"""
        urls = [
            ("https://darwin.md/laptopuri/lenovo-thinkpad-x1-carbon-gen9-i7-16gb-512gb", {
                "brand": "lenovo",
                "model": "x1 carbon",
                "category": "laptops",
                "subcategory": "business"
            })
        ]
        
        for url, expected in urls:
            attrs = self.analyzer.analyze_product_url(url)
            self.assertEqual(attrs.brand, expected["brand"])
            self.assertEqual(attrs.category, expected["category"])
            
    def test_analyze_accessory_url(self):
        """Test pentru analiza URL-urilor de accesorii"""
        urls = [
            ("https://darwin.md/accesorii/husa-iphone-13-pro-spigen-liquid-air-black", {
                "category": "phone_accessories",
                "subcategory": "cases"
            })
        ]
        
        for url, expected in urls:
            attrs = self.analyzer.analyze_product_url(url)
            self.assertEqual(attrs.category, expected["category"])
            self.assertEqual(attrs.subcategory, expected["subcategory"])
            
    def test_analyze_title(self):
        """Test pentru analiza titlurilor de produse"""
        titles = [
            ("Samsung Galaxy S21 Ultra 5G 128GB Black 2021", {
                "brand": "samsung",
                "model": "s21",
                "capacity": "128GB",
                "color": "Black",
                "year": 2021,
                "specs": {"network": "5G"}
            }),
            ("Laptop Lenovo ThinkPad X1 Carbon Gen 9 Intel i7 16GB RAM 512GB SSD", {
                "brand": "lenovo",
                "model": "x1 carbon",
                "specs": {
                    "ram_gb": "16",
                    "storage_gb": "512",
                    "storage_type": "SSD"
                }
            })
        ]
        
        for title, expected in titles:
            attrs = self.analyzer.analyze_product_title(title)
            self.assertEqual(attrs.brand, expected["brand"])
            if "capacity" in expected:
                self.assertEqual(attrs.capacity, expected["capacity"])
            if "year" in expected:
                self.assertEqual(attrs.year, expected["year"])
                
    def test_price_analysis(self):
        """Test pentru analiza prețurilor"""
        prices = [
            ("1299 lei", (1299.0, "MDL")),
            ("1,299.99 MDL", (1299.99, "MDL")),
            ("499 EUR", (499.0, "EUR")),
            ("99.99$", (99.99, "USD"))
        ]
        
        for price_text, expected in prices:
            price, currency = self.analyzer.analyze_price(price_text)
            self.assertEqual(price, expected[0])
            self.assertEqual(currency, expected[1])

if __name__ == '__main__':
    unittest.main()