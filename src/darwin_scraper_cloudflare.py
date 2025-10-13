#!/usr/bin/env python3
"""
Darwin.md AI Web Scraping Agent - Cloudflare Bypass
Enhanced version with advanced Cloudflare protection bypass capabilities
"""

# Import the original scraper
from darwin_scraper_complete import DarwinProductScraper, SELENIUMBASE_AVAILABLE, DRISSIONPAGE_AVAILABLE
import logging
import os
import time
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloudflare_scraper.log'),
        logging.StreamHandler()
    ]
)


class DarwinCloudflareBypass(DarwinProductScraper):
    """
    Enhanced Darwin scraper with advanced Cloudflare bypass capabilities.
    Inherits all functionality from DarwinProductScraper but adds specialized
    extraction methods that are designed to bypass Cloudflare anti-bot protection.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with anti-Cloudflare mode disabled by default"""
        super().__init__(*args, **kwargs)
        self.force_anti_cloudflare = False
        logging.info("CloudflareBypass initialized (anti-Cloudflare mode disabled by default)")
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)

    def _extract_product_details_impl(self, product_url: str) -> dict:
        """
        Override the core extraction logic to prioritize anti-Cloudflare methods when enabled.
        This checks if anti-Cloudflare mode is enabled and uses specialized methods first.
        """
        try:
            # Validare input
            if not product_url or not isinstance(product_url, str):
                raise ValueError("URL invalid furnizat")

            # Încearcă mai multe metode de extragere pentru rata maximă de succes
            product_data = None

            # Verifică dacă ar trebui să folosim metoda anti-Cloudflare
            if self.force_anti_cloudflare:
                # Încearcă mai întâi metodele avansate anti-Cloudflare
                if SELENIUMBASE_AVAILABLE:
                    try:
                        product_data = self._extract_with_seleniumbase_advanced(product_url)
                        if product_data and not product_data.get("error"):
                            product_data["extraction_method"] = "seleniumbase_advanced"
                    except Exception as e:
                        logging.warning(f"Advanced SeleniumBase failed for {product_url}: {str(e)}")

                if DRISSIONPAGE_AVAILABLE and (not product_data or product_data.get("error")):
                    try:
                        product_data = self._extract_with_drissionpage_advanced(product_url)
                        if product_data and not product_data.get("error"):
                            product_data["extraction_method"] = "drissionpage_advanced"
                    except Exception as e:
                        logging.warning(f"Advanced DrissionPage failed for {product_url}: {str(e)}")

            # Fallback to standard extraction methods if advanced methods failed or are not enabled
            if not product_data or product_data.get("error"):
                return super()._extract_product_details_impl(product_url)
            
            return product_data

        except Exception as e:
            error_msg = f"Eroare la extragerea produsului {product_url}: {str(e)}"
            logging.error(error_msg)
            self.failed_urls.append(product_url)
            self.scraping_stats["failed_extractions"] += 1
            return {"error": str(e), "url": product_url}
            
    def _extract_with_seleniumbase_advanced(self, url: str) -> dict:
        """
        Extrage datele produsului folosind SeleniumBase cu tehnici anti-Cloudflare avansate.
        Utilizează browser vizibil (headless=False), delay-uri realiste, și simulează comportament uman.
        """
        try:
            # Folosește browser vizibil pentru a evita detecția headless și uc=True pentru Chromium nemodificat
            with SB(uc=True, test=False, headless=False) as sb:
                # User agent modern
                sb.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                
                # Deschide pagina cu timp de așteptare suficient
                sb.open(url)
                
                # Delay realist pentru a permite încărcarea paginii și posibile challenge-uri
                time.sleep(3)
                
                # Verifică dacă există vreun challenge Cloudflare
                cloudflare_selectors = [
                    "#challenge-running", 
                    ".ray_id", 
                    ".cf-browser-verification", 
                    "#cf-please-wait"
                ]
                
                for selector in cloudflare_selectors:
                    try:
                        if sb.is_element_visible(selector):
                            logging.info(f"Cloudflare detectat ({selector}), așteptăm...")
                            # Delay mai mare pentru challenge
                            time.sleep(10)
                            break
                    except Exception:
                        pass
                
                # Simulează scroll pentru a părea mai uman și a declanșa încărcări lazy
                try:
                    sb.execute_script("window.scrollTo(0, document.body.scrollHeight/3)")
                    time.sleep(1)
                    sb.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
                    time.sleep(1)
                    sb.execute_script("window.scrollTo(0, 0)")
                    time.sleep(1)
                except Exception:
                    pass
                
                # Așteaptă ca pagina să fie complet încărcată
                sb.wait_for_ready_state_complete()
                
                # Extrage datele produsului
                name = self._extract_name_selenium(sb)
                description = self._extract_description_selenium(sb)
                price = self._extract_price_selenium(sb)
                category = self._extract_category_selenium(sb)
                image_url = self._extract_image_selenium(sb)
                availability = self._extract_availability_selenium(sb)
                last_updated = ""
                
                # Încearcă să găsească data ultimei actualizări
                try:
                    el = sb.find_element('time')
                    if el and el.text:
                        last_updated = el.text.strip()
                except Exception:
                    pass
                    
                # Salvează screenshot pentru debugging (opțional)
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshots/cloudflare_test_{timestamp}.png"
                    sb.save_screenshot(filename)
                    logging.info(f"Screenshot salvat: {filename}")
                except Exception as e:
                    logging.warning(f"Nu s-a putut salva screenshot: {e}")

                return {
                    "url": url,
                    "name": name,
                    "description": description,
                    "price": price,
                    "category": category,
                    "image_url": image_url,
                    "availability": availability,
                    "last_updated": last_updated,
                    "in_stock": self._normalize_in_stock(availability),
                    "bypass_method": "seleniumbase_advanced"
                }
                
        except Exception as e:
            logging.error(f"Eroare în _extract_with_seleniumbase_advanced: {e}")
            return {"error": str(e), "url": url}
            
    def _extract_with_drissionpage_advanced(self, url: str) -> dict:
        """
        Extrage datele produsului folosind DrissionPage cu tehnici anti-Cloudflare avansate.
        """
        page = None
        try:
            # Configurare avansată pentru DrissionPage
            if not DRISSIONPAGE_AVAILABLE:
                raise ImportError("DrissionPage nu este disponibil")
                
            from DrissionPage.easy_set import set_headless
            # Folosește browser vizibil
            set_headless(False)
            from DrissionPage import MixPage
            page = MixPage()
            
            # Setări pentru evitarea detecției automatizării
            page.set.cookies_when_connect = True
            
            # User agent modern
            page.set.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            
            # Încarcă pagina
            page.get(url)
            
            # Delay pentru a permite încărcarea completă și challenge-uri
            time.sleep(3)
            
            # Verifică elemente Cloudflare
            cloudflare_selectors = [
                "#challenge-running", 
                ".ray_id", 
                ".cf-browser-verification", 
                "#cf-please-wait"
            ]
            
            for selector in cloudflare_selectors:
                try:
                    cf_element = page.ele(selector, timeout=1)
                    if cf_element:
                        logging.info(f"Cloudflare detectat ({selector}), așteptăm...")
                        time.sleep(10)
                        break
                except Exception:
                    pass
                    
            # Simulează comportament uman cu scroll
            try:
                page.scroll.to_bottom(smooth=True)
                time.sleep(1)
                page.scroll.to_top(smooth=True)
            except Exception:
                pass
                
            # Extrage informațiile produsului
            name = self._extract_name_drission(page)
            description = self._extract_description_drission(page)
            price = self._extract_price_drission(page)
            category = self._extract_category_drission(page)
            image_url = self._extract_image_drission(page)
            availability = self._extract_availability_drission(page)
            last_updated = ""
            
            try:
                t = page.ele('time')
                if t and getattr(t, 'text', '').strip():
                    last_updated = t.text.strip()
            except Exception:
                pass
                
            # Salvează screenshot (opțional)
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs("screenshots", exist_ok=True)
                page.save_screenshot(f"screenshots/drission_cf_{timestamp}.png")
            except Exception:
                pass

            return {
                "url": url,
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "image_url": image_url,
                "availability": availability,
                "last_updated": last_updated,
                "in_stock": self._normalize_in_stock(availability),
                "bypass_method": "drissionpage_advanced"
            }
            
        except Exception as e:
            logging.error(f"Eroare în _extract_with_drissionpage_advanced: {e}")
            return {"error": str(e), "url": url}
        finally:
            try:
                if page:
                    page.quit()
            except Exception:
                pass
                
    def enable_anti_cloudflare(self):
        """Activează modul avansat anti-Cloudflare pentru toate cererile viitoare"""
        self.force_anti_cloudflare = True
        logging.info("Mod anti-Cloudflare activat")
        
    def disable_anti_cloudflare(self):
        """Dezactivează modul avansat anti-Cloudflare"""
        self.force_anti_cloudflare = False
        logging.info("Mod anti-Cloudflare dezactivat")
        
    def test_cloudflare_bypass(self, url: str) -> dict:
        """
        Testează bypass-ul Cloudflare pe o anumită adresă URL.
        Încearcă ambele metode de extracție avansată și returnează rezultate detaliate.
        
        Args:
            url: URL-ul de testat
            
        Returns:
            Rezultate detaliate despre succesul bypass-ului și datele extrase
        """
        results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "seleniumbase_result": None,
            "drissionpage_result": None,
            "successful_method": None,
            "cloudflare_detected": False,
            "screenshots": [],
        }
        
        # Testează SeleniumBase dacă este disponibil
        if SELENIUMBASE_AVAILABLE:
            try:
                sb_result = self._extract_with_seleniumbase_advanced(url)
                results["seleniumbase_result"] = sb_result
                if not sb_result.get("error"):
                    results["successful_method"] = "seleniumbase"
            except Exception as e:
                results["seleniumbase_result"] = {"error": str(e)}
                
        # Testează DrissionPage dacă este disponibil
        if DRISSIONPAGE_AVAILABLE:
            try:
                dp_result = self._extract_with_drissionpage_advanced(url)
                results["drissionpage_result"] = dp_result
                if not dp_result.get("error") and not results["successful_method"]:
                    results["successful_method"] = "drissionpage"
            except Exception as e:
                results["drissionpage_result"] = {"error": str(e)}
                
        # Verifică dacă s-au creat screenshot-uri
        try:
            for filename in os.listdir("screenshots"):
                if filename.startswith("cloudflare_test_") or filename.startswith("drission_cf_"):
                    if datetime.now().strftime("%Y%m%d") in filename:
                        results["screenshots"].append(f"screenshots/{filename}")
        except Exception:
            pass
            
        # Determină succesul final
        results["success"] = bool(results["successful_method"])
        
        return results

# Exemplu de utilizare directă
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Darwin.md Cloudflare Bypass Tester")
    parser.add_argument("--url", type=str, help="URL to test Cloudflare bypass on", 
                        default="https://darwin.md/telefoane/smartphone")
    parser.add_argument("--method", type=str, choices=["seleniumbase", "drissionpage", "both"], 
                        default="both", help="Which method to use for testing")
    
    args = parser.parse_args()
    
    # Initialize scraper - using a dummy API key if needed
    scraper = DarwinCloudflareBypass("dummy_key")
    scraper.enable_anti_cloudflare()
    
    print(f"Testing Cloudflare bypass on: {args.url}")
    
    if args.method == "both" or args.method == "seleniumbase":
        if SELENIUMBASE_AVAILABLE:
            print("\n--- Testing SeleniumBase Advanced Method ---")
            try:
                result = scraper._extract_with_seleniumbase_advanced(args.url)
                if not result.get("error"):
                    print("✅ Success! Extracted product data:")
                    for key, value in result.items():
                        if key in ["name", "price", "category", "availability"]:
                            print(f"  {key}: {value}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Exception: {e}")
        else:
            print("❌ SeleniumBase is not available")
    
    if args.method == "both" or args.method == "drissionpage":
        if DRISSIONPAGE_AVAILABLE:
            print("\n--- Testing DrissionPage Advanced Method ---")
            try:
                result = scraper._extract_with_drissionpage_advanced(args.url)
                if not result.get("error"):
                    print("✅ Success! Extracted product data:")
                    for key, value in result.items():
                        if key in ["name", "price", "category", "availability"]:
                            print(f"  {key}: {value}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Exception: {e}")
        else:
            print("❌ DrissionPage is not available")
    
    print("\nCheck the 'screenshots' directory for visual confirmation of the bypass")