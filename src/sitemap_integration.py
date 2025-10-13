"""
Patch pentru integrarea noului procesor de sitemap în DarwinProductScraper
"""

from typing import Dict, Any
from darwin_sitemap_processor import DarwinSitemapProcessor

class SitemapIntegrationMixin:
    """Mixin pentru integrarea noului procesor de sitemap"""
    
    def _discover_impl(self, sitemap_url: str = "https://darwin.md/sitemap.xml") -> Dict[str, Any]:
        """
        Implementare îmbunătățită pentru descoperirea URL-urilor folosind noul procesor
        """
        try:
            processor = DarwinSitemapProcessor(
                max_workers=20,  # Mai mulți workers pentru procesare mai rapidă
                request_delay=0.2  # Delay mai mic între request-uri
            )
            
            result = processor.process_sitemap_index(sitemap_url)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Eroare la procesarea sitemap"),
                    "sitemap_url": sitemap_url
                }
            
            # Actualizează statisticile
            self.scraping_stats["urls_discovered"] = result["total_urls"]
            
            # Adaugă categoriile găsite
            for category in result["categories"].keys():
                self.categories_found.add(category)
            
            return {
                "success": True,
                "sitemap_url": sitemap_url,
                "total_urls_found": result["total_urls"],
                "product_urls": result["urls"],
                "product_count": result["total_urls"],
                "categories": result["categories"],
                "non_product_urls": 0  # Toate URL-urile sunt deja filtrate ca produse
            }
            
        except Exception as e:
            self.logger.exception("Eroare la accesarea sitemap-ului")
            return {"success": False, "error": str(e), "sitemap_url": sitemap_url}