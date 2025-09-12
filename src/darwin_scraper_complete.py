#!/usr/bin/env python3
"""
Darwin.md AI Web Scraping Agent - Versiune Completă și Reparată
Agent inteligent specializat pentru Darwin.md cu toate metodele implementate
"""

import streamlit as st
import requests
import json
import time
import csv
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional
import re
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import re
import time
import logging
import xml.etree.ElementTree as ET
import streamlit as st

# AI Framework
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

# Web scraping libraries
try:
    from seleniumbase import SB
    SELENIUMBASE_AVAILABLE = True
except ImportError:
    SELENIUMBASE_AVAILABLE = False
    
try:
    from DrissionPage import ChromiumPage, SessionPage, MixPage
    DRISSIONPAGE_AVAILABLE = True
except ImportError:
    DRISSIONPAGE_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class DarwinProductScraper:
    """
    Scraper profesional pentru e-commerce specializat pentru Darwin.md
    Construit pentru integrarea cu Telegram Bot + ChromaDB
    """
    
    def __init__(self, openai_api_key: str, openai_model: str = "gpt-4o"):
        """Inițializare scraper cu integrare OpenAI"""
        
        if not openai_api_key:
            raise ValueError("OpenAI API key este necesar")
        
        # Configurare Model OpenAI
        self.model = OpenAIChat(
            id=openai_model,
            api_key=openai_api_key,
            temperature=0.1
        )
        
        # Agent AI cu instrumente specializate
        self.agent = Agent(
            model=self.model,
            tools=[
                self.discover_all_products,
                self.extract_product_details,
                self.validate_product_data,
                self.analyze_darwin_categories
            ],
            instructions="""
            Ești un specialist profesional în extragerea datelor pentru e-commerce pentru Darwin.md.
            
            OBIECTIV: Extrage catalogul complet de produse pentru Telegram Bot + ChromaDB
            
            SITE ȚINTĂ: Darwin.md (retailer de electronice din Moldova)
            SITEMAP: https://darwin.md/sitemap.xml
            
            CATEGORII DE PRODUSE DE AȘTEPTAT:
            - Telefoane (Smartphone-uri)
            - Laptopuri (Laptopuri) 
            - Tablete (Tablete)
            - Accesorii (Accesorii)
            - Audio (Căști, Boxe)
            - Gaming (Console, Jocuri)
            - Smart Home
            - Electronice (Electronice Generale)
            
            CERINȚE DE CALITATE A DATELOR:
            - Nume de produse curate și structurate
            - Prețuri precise în MDL (Leu Moldovenesc)
            - Descrieri comprehensive
            - URL-uri valide de produse
            - URL-uri de imagini de înaltă calitate
            - Categorizare adecvată
            
            FORMAT IEȘIRE: CSV gata pentru colecțiile ChromaDB
            COLOANE: id, name, description, price, category, url, image_url
            """
        )
        
        # Stocare date
        self.all_products = []
        self.failed_urls = []
        self.categories_found = set()
        self.scraping_stats = {
            "urls_discovered": 0,
            "products_extracted": 0,
            "failed_extractions": 0,
            "categories_found": 0,
            "start_time": None,
            "end_time": None
        }

    def discover_all_products_raw(self, sitemap_url: str = "https://darwin.md/sitemap.xml") -> Dict[str, Any]:
        """
        Reliable caller for sitemap discovery that avoids issues with @tool wrappers.
        This will try several strategies to invoke the underlying implementation:
        1) call the instance attribute if callable
        2) unwrap common decorator attributes (__wrapped__, func, fn)
        3) bind the raw function to the instance and call it
        Returns the same dict as `discover_all_products`.
        """
        # Strategy 1: call instance attribute
        try:
            inst_attr = getattr(self, 'discover_all_products', None)
            if callable(inst_attr):
                try:
                    return inst_attr(sitemap_url)
                except TypeError:
                    # wrapper may not accept arguments directly
                    try:
                        return inst_attr()
                    except Exception:
                        pass
        except Exception:
            pass

        # Strategy 2: try to get the raw function from the class dict and unwrap
        raw = self.__class__.__dict__.get('discover_all_products')
        if raw is None:
            return {"success": False, "error": "discover_all_products not found on class"}

        # Try a sequence of possible call patterns used by decorators/wrappers
        call_attempts = []

        # 1) instance attribute (may be wrapper)
        try:
            inst_attr = getattr(self, 'discover_all_products', None)
            call_attempts.append(("inst_attr(sitemap_url)", lambda: inst_attr(sitemap_url)))
            call_attempts.append(("inst_attr()", lambda: inst_attr()))
        except Exception:
            pass

        # 2) raw called with self
        try:
            call_attempts.append(("raw(self, sitemap_url)", lambda: raw(self, sitemap_url)))
            call_attempts.append(("raw(self)", lambda: raw(self)))
            call_attempts.append(("raw(sitemap_url)", lambda: raw(sitemap_url)))
            call_attempts.append(("raw()", lambda: raw()))
        except Exception:
            pass

        # 3) common attributes on wrapper
        for attrname in ('__wrapped__', 'func', 'fn', 'function'):
            try:
                inner = getattr(raw, attrname, None)
                if inner:
                    call_attempts.append((f"{attrname}(self, sitemap_url)", lambda inner=inner: inner(self, sitemap_url)))
                    call_attempts.append((f"{attrname}(sitemap_url)", lambda inner=inner: inner(sitemap_url)))
            except Exception:
                continue

        # Execute attempts until one succeeds
        for desc, fn in call_attempts:
            try:
                res = fn()
                if res is not None:
                    return res
            except Exception:
                # ignore and try next
                continue

        # If we reached here, all attempts failed
        return {"success": False, "error": "Failed to invoke discover_all_products via known wrappers"}
    
    @tool(description="Descoperă toate URL-urile de produse din sitemap-ul Darwin.md")
    def discover_all_products(self, sitemap_url: str = "https://darwin.md/sitemap.xml") -> Dict[str, Any]:
        """
        Descoperă toate URL-urile de produse din sitemap-ul Darwin.md
        
        Args:
            sitemap_url: URL către sitemap-ul Darwin.md
            
        Returns:
            Dict conținând URL-urile descoperite și metadatele
        """
        # Forward to the non-decorated implementation which contains the parsing logic.
        return self._discover_impl(sitemap_url)

    def _discover_impl(self, sitemap_url: str = "https://darwin.md/sitemap.xml") -> Dict[str, Any]:
        """Non-decorated sitemap parser. Fetches sitemap(s), extracts URLs,
        filters product-like URLs and returns a summary dict. Safe to call from scripts.
        """
        try:
            if 'st' in globals():
                st.info(f"🗺️ Accesez sitemap-ul Darwin.md: {sitemap_url}")

            logging.info(f"Accesez sitemap-ul: {sitemap_url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(sitemap_url, headers=headers, timeout=20)
            resp.raise_for_status()

            root = ET.fromstring(resp.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            all_urls: List[str] = []

            # If sitemap index (has <sitemap> entries)
            sitemap_entries = root.findall('.//ns:sitemap', namespace)
            if sitemap_entries:
                for s_elem in sitemap_entries:
                    loc = s_elem.find('ns:loc', namespace)
                    if loc is None or not loc.text:
                        continue
                    sub_url = loc.text.strip()
                    try:
                        sub_urls = self._parse_single_sitemap(sub_url)
                        if sub_urls:
                            all_urls.extend(sub_urls)
                    except Exception:
                        # fallback: try inline fetch
                        try:
                            r2 = requests.get(sub_url, headers=headers, timeout=15)
                            r2.raise_for_status()
                            subroot = ET.fromstring(r2.content)
                            url_elems = subroot.findall('.//ns:url', namespace)
                            for ue in url_elems:
                                loc2 = ue.find('ns:loc', namespace)
                                if loc2 is not None and loc2.text:
                                    all_urls.append(loc2.text.strip())
                        except Exception:
                            continue
            else:
                # direct urlset
                url_elements = root.findall('.//ns:url', namespace)
                for url_elem in url_elements:
                    loc_elem = url_elem.find('ns:loc', namespace)
                    if loc_elem is not None and loc_elem.text:
                        all_urls.append(loc_elem.text.strip())

            # Deduplicate preserving order
            seen = set()
            deduped = []
            for u in all_urls:
                if u and u not in seen:
                    seen.add(u)
                    deduped.append(u)

            product_urls = [u for u in deduped if self._is_darwin_product_url(u)]

            self.scraping_stats["urls_discovered"] = len(product_urls)

            return {
                "success": True,
                "sitemap_url": sitemap_url,
                "total_urls_found": len(deduped),
                "product_urls": product_urls,
                "product_count": len(product_urls),
                "non_product_urls": len(deduped) - len(product_urls)
            }
        except Exception as e:
            logging.exception("Eroare la accesarea sitemap-ului")
            return {"success": False, "error": str(e), "sitemap_url": sitemap_url}
    
    def _is_darwin_product_url(self, url: str) -> bool:
        """
        Determină dacă un URL este o pagină de produs Darwin.md
        
        Args:
            url: URL de verificat
            
        Returns:
            bool: True dacă URL-ul pare să fie o pagină de produs
        """
        if not url or not url.startswith('https://darwin.md'):
            return False
        
        url_lower = url.lower()
        
        # Modele specifice de produse Darwin.md (bazate pe sitemap-ul real)
        product_indicators = [
            '/telefoane/',
            '/laptopuri/', 
            '/tablete/',
            '/accesorii/',
            '/audio/',
            '/gaming/',
            '/smart-home/',
            '/electronice/',
            '/produse/',
            '/product/',
            '/monitoare/',
            '/smartphone/',
            '/casti/',
            '/boxe/',
            '/sisteme-pc/',
            '/imprimante/',
            '/periferice-pc/',
            '/componente-pc/',
            '/camere-foto/',
            '/tehnica-bucatarie/',
            '/aspiratoare/',
            '/aparate-fitness/',
            '/transport-personal/',
            '/telefoane-mobile-cu-buton-',
            '/telefoane-dect-',
            '/sticle-si-folii-de-protectie-',
            '/cabluri-',
            '/incarcatoare-',
            '/huse-pentru-smartphone-',
            '/power-bank-',
            '/ceasuri-inteligente-',
            '/bratari-inteligente-',
            '/drone-',
            '/ochelari-vr-'
        ]
        
        # Verifică indicatorii de produse (meciuri generale)
        has_product_pattern = any(pattern in url_lower for pattern in product_indicators)

        # Verifică modelul ID produs (ex: URL se termină cu /123 sau ?id=123)
        has_product_id = bool(re.search(r'/\d+/?$', url_lower)) or bool(re.search(r'[?&]id=\d+', url_lower))

        # Verifică segmente explicite de produs (mai stricte)
        explicit_product_segments = ['/product/', '/produs/', '/p/', '/item/', '/products/']
        has_explicit_segment = any(seg in url_lower for seg in explicit_product_segments)

        # Verifică sufixuri comune de slug cu id (ex: some-name-123)
        slug_with_number = bool(re.search(r'-\d+/?$', url_lower))

        # Exclude paginile non-produs
        exclude_patterns = [
            '/contact', '/about', '/search', '/cart', '/checkout',
            '/login', '/register', '/blog', '/news', '/help',
            '/terms', '/privacy', '/sitemap', '/rss',
            '.css', '.js', '.xml', '.pdf', '.jpg', '.png', '.gif',
            '/categories.xml', '/blogs.xml', '/seo_filters.xml',
            '/promos.xml', '/pages.xml'
        ]

        has_exclusion = any(pattern in url_lower for pattern in exclude_patterns)

        # Stricter rule: require explicit product segment, numeric id, or slug-with-number
        is_probable_product = has_explicit_segment or has_product_id or slug_with_number

        return is_probable_product and not has_exclusion

    @tool(description="Extrage informații detaliate despre produse din pagina de produs Darwin.md")
    def extract_product_details(self, product_url: str) -> Dict[str, Any]:
        """
        Extrage detalii complete despre produse dintr-o pagină de produs Darwin.md
        
        Args:
            product_url: URL-ul paginii de produs
            
        Returns:
            Dict conținând informațiile extrase despre produs
        """
        # Forward to the non-decorated implementation so extraction can be invoked
        # programmatically from scripts without dealing with decorator wrappers.
        return self._extract_product_details_impl(product_url)

    def _extract_product_details_impl(self, product_url: str) -> Dict[str, Any]:
        """Core extraction logic (non-decorated). Attempts multiple extraction
        backends (DrissionPage, SeleniumBase, Requests+BeautifulSoup) and
        returns a product dict or an error dict.
        """
        try:
            # Validare input
            if not product_url or not isinstance(product_url, str):
                raise ValueError("URL invalid furnizat")

            # Încearcă mai multe metode de extragere pentru rata maximă de succes
            product_data = None

            # Metoda 1: DrissionPage (cea mai rapidă)
            if DRISSIONPAGE_AVAILABLE and not product_data:
                try:
                    product_data = self._extract_with_drissionpage(product_url)
                    if product_data and not product_data.get("error"):
                        product_data["extraction_method"] = "drissionpage"
                except Exception as e:
                    logging.warning(f"DrissionPage failed for {product_url}: {str(e)}")

            # Metoda 2: SeleniumBase (cea mai fiabilă pentru JS)
            if SELENIUMBASE_AVAILABLE and (not product_data or product_data.get("error")):
                try:
                    product_data = self._extract_with_seleniumbase(product_url)
                    if product_data and not product_data.get("error"):
                        product_data["extraction_method"] = "seleniumbase"
                except Exception as e:
                    logging.warning(f"SeleniumBase failed for {product_url}: {str(e)}")

            # Metoda 3: Requests + BeautifulSoup (fallback)
            if BEAUTIFULSOUP_AVAILABLE and (not product_data or product_data.get("error")):
                try:
                    product_data = self._extract_with_requests(product_url)
                    if product_data and not product_data.get("error"):
                        product_data["extraction_method"] = "requests"
                except Exception as e:
                    logging.warning(f"Requests failed for {product_url}: {str(e)}")

            if not product_data or product_data.get("error"):
                self.failed_urls.append(product_url)
                self.scraping_stats["failed_extractions"] += 1
                return {"error": "Toate metodele de extragere au eșuat", "url": product_url}

            # Adaugă la categoriile găsite
            if product_data.get("category"):
                self.categories_found.add(product_data["category"])

            self.scraping_stats["products_extracted"] += 1
            return product_data

        except Exception as e:
            error_msg = f"Eroare la extragerea produsului {product_url}: {str(e)}"
            logging.error(error_msg)
            self.failed_urls.append(product_url)
            self.scraping_stats["failed_extractions"] += 1
            return {"error": str(e), "url": product_url}
    
    def _extract_with_drissionpage(self, url: str) -> Dict[str, Any]:
        """Extrage datele produsului folosind DrissionPage"""
        page = None
        try:
            page = MixPage()
            page.get(url)
            time.sleep(2)  # Permite încărcarea paginii
            
            name = self._extract_name_drission(page)
            description = self._extract_description_drission(page)
            price = self._extract_price_drission(page)
            category = self._extract_category_drission(page)
            image_url = self._extract_image_drission(page)
            availability = self._extract_availability_drission(page)
            last_updated = ""
            try:
                # Try common time/meta selectors on page object
                try:
                    t = page.ele('time')
                    if t and getattr(t, 'text', '').strip():
                        last_updated = t.text.strip()
                except Exception:
                    pass

            except Exception:
                last_updated = ""

            return {
                "url": url,
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "image_url": image_url,
                "availability": availability,
                "last_updated": last_updated,
                "in_stock": self._normalize_in_stock(availability)
            }
            
        except Exception as e:
            return {"error": str(e), "url": url}
        finally:
            try:
                if page:
                    page.quit()
            except Exception:
                pass
    
    def _extract_with_seleniumbase(self, url: str) -> Dict[str, Any]:
        """Extrage datele produsului folosind SeleniumBase"""
        try:
            with SB(uc=True, test=True, headless=True) as sb:
                sb.open(url)
                sb.wait_for_ready_state_complete()
                time.sleep(2)
                
                name = self._extract_name_selenium(sb)
                description = self._extract_description_selenium(sb)
                price = self._extract_price_selenium(sb)
                category = self._extract_category_selenium(sb)
                image_url = self._extract_image_selenium(sb)
                availability = self._extract_availability_selenium(sb)
                last_updated = ""
                try:
                    # Try to find time element
                    try:
                        el = sb.find_element('time')
                        if el and el.text:
                            last_updated = el.text.strip()
                    except Exception:
                        pass
                except Exception:
                    last_updated = ""

                return {
                    "url": url,
                    "name": name,
                    "description": description,
                    "price": price,
                    "category": category,
                    "image_url": image_url,
                    "availability": availability,
                    "last_updated": last_updated,
                    "in_stock": self._normalize_in_stock(availability)
                }
                
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def _extract_with_requests(self, url: str) -> Dict[str, Any]:
        """Extrage datele produsului folosind requests + BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ro-RO,ro;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')

            name = self._extract_name_soup(soup)
            description = self._extract_description_soup(soup)
            price = self._extract_price_soup(soup)
            category = self._extract_category_soup(soup)
            image_url = self._extract_image_soup(soup, url)
            availability = self._extract_availability_soup(soup)
            last_updated = self._extract_last_updated_soup(soup, headers=response.headers if hasattr(response, 'headers') else None)
            in_stock = self._normalize_in_stock(availability)

            # Structured data / meta fallback (JSON-LD, meta tags)
            try:
                sd = self._parse_structured_data_from_html(response.content)
                if sd:
                    if (not price or price == 'Preț indisponibil') and sd.get('price'):
                        price = sd.get('price')
                    if (not description or description == 'Nu există descriere disponibilă') and sd.get('description'):
                        description = sd.get('description')
                    if (not name or name == 'Produs Necunoscut') and sd.get('name'):
                        name = sd.get('name')
                    if (not image_url) and sd.get('image'):
                        image_url = sd.get('image')
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
                "in_stock": in_stock
            }
            
        except Exception as e:
            return {"error": str(e), "url": url}
    
    # ==============================================
    # METODE DE EXTRAGERE DRISSIONPAGE
    # ==============================================
    
    def _extract_name_drission(self, page) -> str:
        """Extrage numele produsului folosind DrissionPage"""
        selectors = [
            'h1.product-title',
            'h1[data-testid="product-title"]',
            'h1.title',
            '.product-name h1',
            'h1',
            '.product-title',
            '[data-testid="product-name"]',
            '.product-head h1',
            '.product-info h1',
            '.product-details h1'
        ]
        
        for selector in selectors:
            try:
                element = page.ele(selector)
                if element and element.text.strip():
                    return element.text.strip()
            except Exception:
                continue
        
        # Fallback la titlul paginii
        try:
            title = page.title
            if title:
                # Curăță titlul (elimină numele site-ului, etc.)
                clean_title = title.split('|')[0].split('-')[0].strip()
                if clean_title and clean_title.lower() != 'darwin':
                    return clean_title
        except Exception:
            pass
        
        return "Produs Necunoscut"
    
    def _extract_description_drission(self, page) -> str:
        """Extrage descrierea produsului folosind DrissionPage"""
        selectors = [
            '.product-description',
            '.description',
            '.product-details',
            '.product-info',
            '[data-testid="description"]',
            '.specifications',
            '.features',
            '.product-content',
            '.product-desc',
            '.product-summary'
        ]
        
        for selector in selectors:
            try:
                element = page.ele(selector)
                if element and element.text.strip():
                    desc = element.text.strip()
                    # Limitează lungimea descrierii
                    return desc[:500] + "..." if len(desc) > 500 else desc
            except Exception:
                continue
        
        return "Nu există descriere disponibilă"
    
    def _extract_price_drission(self, page) -> str:
        """Extrage prețul produsului folosind DrissionPage"""
        price_selectors = [
            '.price-current',
            '.price',
            '.product-price',
            '[data-testid="price"]',
            '.sale-price',
            '.regular-price',
            '.amount',
            '.price-box .price',
            '.current-price',
            '.final-price',
            '.price-value'
        ]
        
        for selector in price_selectors:
            try:
                elements = page.eles(selector)
                for element in elements:
                    text = element.text.strip()
                    # Caută modelul de preț MDL
                    price_match = re.search(r'(\d+[.,]?\d*)\s*(lei|mdl)', text.lower())
                    if price_match:
                        price_num = price_match.group(1).replace(',', '.')
                        return f"{price_num} MDL"
                    
                    # Caută orice preț numeric
                    number_match = re.search(r'(\d+[.,]?\d*)', text)
                    if number_match and len(text) < 20:  # Evită potrivirea șirurilor lungi
                        price_num = number_match.group(1).replace(',', '.')
                        return f"{price_num} MDL"
            except Exception:
                continue
        
        # Fallback: caută în întregul text al paginii pentru modele de preț
        try:
            full_text = ''
            try:
                full_text = page.get_text()
            except Exception:
                try:
                    full_text = page.html
                except Exception:
                    full_text = ''

            price_match = re.search(r"(\d+[\.,]?\d*)\s*(lei|mdl|mdL|ron|eur|€|usd|\$)", full_text.lower())
            if price_match:
                number = price_match.group(1).replace(',', '.')
                currency = price_match.group(2).upper()
                # Normalize common tokens
                if currency in ('LEI', 'MDL', 'MDL'):
                    currency = 'MDL'
                elif currency in ('EUR', '€'):
                    currency = 'EUR'
                elif currency in ('USD', '$'):
                    currency = 'USD'
                return f"{number} {currency}"
        except Exception:
            pass

        return "Preț indisponibil"
    
    def _extract_category_drission(self, page) -> str:
        """Extrage categoria produsului folosind DrissionPage"""
        # Încearcă breadcrumbs mai întâi
        breadcrumb_selectors = [
            '.breadcrumb a',
            '.breadcrumbs a',
            '.nav-breadcrumb a',
            '[data-testid="breadcrumb"] a',
            '.breadcrumb-item a',
            '.breadcrumb-link'
        ]
        
        for selector in breadcrumb_selectors:
            try:
                elements = page.eles(selector)
                if elements and len(elements) > 1:
                    # Ia ultimul breadcrumb semnificativ (excluzând "Home")
                    for elem in reversed(elements):
                        text = elem.text.strip()
                        if text.lower() not in ['home', 'acasa', 'principal', 'darwin', 'index']:
                            return text
            except Exception:
                continue
        
        # Fallback: extrage din URL
        url_parts = page.url.split('/')
        for part in url_parts:
            if part and not part.isdigit():
                clean_part = part.replace('-', ' ').replace('_', ' ').title()
                # Mapare categorii românești
                category_map = {
                    'telefoane': 'Telefoane',
                    'smartphone': 'Smartphone-uri',
                    'laptopuri': 'Laptopuri',
                    'tablete': 'Tablete',
                    'accesorii': 'Accesorii',
                    'audio': 'Audio',
                    'casti': 'Căști',
                    'boxe': 'Boxe',
                    'gaming': 'Gaming',
                    'monitoare': 'Monitoare',
                    'sisteme pc': 'Sisteme PC',
                    'componente pc': 'Componente PC'
                }
                
                clean_lower = clean_part.lower()
                if clean_lower in category_map:
                    return category_map[clean_lower]
                elif len(clean_part) > 3:
                    return clean_part
        
        return "Electronice"
    
    def _extract_image_drission(self, page) -> str:
        """Extrage imaginea principală a produsului folosind DrissionPage"""
        img_selectors = [
            '.product-image img',
            '.main-image img',
            '.product-photo img',
            '[data-testid="product-image"] img',
            '.gallery img:first-child',
            '.product-gallery img:first-child',
            '.product-images img',
            '.product-media img'
        ]
        
        for selector in img_selectors:
            try:
                element = page.ele(selector)
                if element:
                    src = element.attr('src') or element.attr('data-src') or element.attr('data-original')
                    if src and not src.endswith('.svg'):
                        # Fă URL-ul absolut
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = urljoin(page.url, src)
                        return src
            except Exception:
                continue
        
        return ""
    
    def _extract_availability_drission(self, page) -> str:
        """Extrage disponibilitatea produsului folosind DrissionPage"""
        availability_selectors = [
            '.availability',
            '.stock-status',
            '.in-stock',
            '.out-of-stock',
            '[data-testid="availability"]',
            '.product-availability',
            '.stock-info'
        ]
        
        for selector in availability_selectors:
            try:
                element = page.ele(selector)
                if element and element.text.strip():
                    status = element.text.strip()
                    # Mapare status-uri românești
                    if any(word in status.lower() for word in ['disponibil', 'in stoc', 'pe stoc']):
                        return "În stoc"
                    elif any(word in status.lower() for word in ['indisponibil', 'lipsa', 'epuizat']):
                        return "Indisponibil"
                    else:
                        return status
            except Exception:
                continue
        
        return "Necunoscut"

    def _parse_structured_data_from_html(self, html_content) -> Dict[str, Any]:
        """Parses JSON-LD and common meta tags from HTML content to extract name, price, description, image."""
        try:
            text = html_content
            if isinstance(html_content, bytes):
                text = html_content.decode('utf-8', errors='ignore')

            results = {}
            # JSON-LD
            for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, flags=re.S | re.I):
                try:
                    jd = json.loads(m.group(1).strip())
                    # If it's a list, check entries
                    candidates = jd if isinstance(jd, list) else [jd]
                    for entry in candidates:
                        if isinstance(entry, dict):
                            if 'offers' in entry:
                                offers = entry.get('offers')
                                if isinstance(offers, dict):
                                    price = offers.get('price') or offers.get('priceSpecification', {}).get('price')
                                    if price:
                                        results['price'] = str(price)
                            if not results.get('name') and entry.get('name'):
                                results['name'] = entry.get('name')
                            if not results.get('description') and entry.get('description'):
                                results['description'] = entry.get('description')
                            if not results.get('image') and entry.get('image'):
                                results['image'] = entry.get('image')
                except Exception:
                    continue

            # Meta tags fallback
            if not results.get('name'):
                m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', text, flags=re.I)
                if m:
                    results['name'] = m.group(1)
            if not results.get('description'):
                m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, flags=re.I)
                if m:
                    results['description'] = m.group(1)
            if not results.get('image'):
                m = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', text, flags=re.I)
                if m:
                    results['image'] = m.group(1)

            return results
        except Exception:
            return {}

    def _extract_price_from_text(self, text: str) -> Optional[str]:
        """Extract a price like '99 lei' or '199.99 USD' from arbitrary text and normalize it."""
        if not text:
            return None
        try:
            s = text.lower()
            # Replace non-breaking spaces
            s = s.replace('\u00a0', ' ')
            # Common pattern: number + optional decimals + space + currency
            m = re.search(r"(\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d+)?)[\s\u00A0]*(lei|mdl|ron|eur|€|usd|\$)", s)
            if m:
                number = m.group(1).replace('.', '').replace(',', '.')
                cur = m.group(2).upper()
                if cur in ('LEI', 'MDL', 'RON'):
                    cur = 'MDL'
                elif cur in ('EUR', '€'):
                    cur = 'EUR'
                elif cur in ('USD', '$'):
                    cur = 'USD'
                return f"{number} {cur}"
            # Try simpler numeric pattern (e.g., '99 lei' without thousands)
            m2 = re.search(r"(\d+[\.,]?\d*)[\s\u00A0]*(lei|mdl|ron|eur|€|usd|\$)", s)
            if m2:
                number = m2.group(1).replace(',', '.')
                cur = m2.group(2).upper()
                if cur in ('LEI', 'MDL', 'RON'):
                    cur = 'MDL'
                elif cur in ('EUR', '€'):
                    cur = 'EUR'
                elif cur in ('USD', '$'):
                    cur = 'USD'
                return f"{number} {cur}"
        except Exception:
            return None
        return None

    def _extract_links_from_listing(self, url: str, max_links: int = 30) -> List[str]:
        """Fetch a listing/category page and return a list of candidate product URLs.

        - Uses requests + BeautifulSoup for speed.
        - Normalizes relative links and filters to darwin.md domain.
        - Applies _is_darwin_product_url as a soft filter; also includes links with
          slug-number patterns or explicit product segments.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = None
            try:
                soup = BeautifulSoup(resp.content, 'html.parser')
            except Exception:
                return []

            found = []
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                if not href:
                    continue
                # normalize
                full = urljoin(url, href)
                parsed = urlparse(full)
                if not parsed.scheme.startswith('http'):
                    continue
                # restrict to darwin.md
                if 'darwin.md' not in parsed.netloc and 'darwin.md' not in full:
                    continue
                # skip anchors and file links
                if any(full.lower().endswith(ext) for ext in ('.jpg','.png','.gif','.pdf','.css','.js')):
                    continue
                # prefer product-like
                if self._is_darwin_product_url(full) or re.search(r'-\d+/?$', full) or '/product/' in full or '/produs/' in full:
                    if full not in found:
                        found.append(full)
                else:
                    # also consider links that look like product detail slugs (long slugs)
                    path = parsed.path or ''
                    if len(path.split('/'))>2 and '-' in path.split('/')[-1] and len(path.split('/')[-1])>6:
                        if full not in found:
                            found.append(full)
                if len(found) >= max_links:
                    break

            # dedupe preserving order
            seen = set(); dedup = []
            for u in found:
                if u not in seen:
                    seen.add(u); dedup.append(u)

            return dedup
        except Exception:
            return []

    def collect_all_product_links_from_listing(self, listing_url: str, max_links: Optional[int] = None, max_pages: int = 20) -> List[str]:
        """Collect all candidate product links from a listing/category page.

        - Follows pagination (rel="next", anchors with 'next' text or common pagination selectors).
        - Uses `_extract_links_from_listing` on each page and deduplicates.
        - Stops when no new pages or when max_pages reached or when max_links reached.
        """
        collected = []
        seen = set()
        to_visit = [listing_url]
        pages_visited = 0

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        while to_visit and (pages_visited < max_pages):
            page_url = to_visit.pop(0)
            pages_visited += 1
            try:
                # extract product-like links from this page
                links = self._extract_links_from_listing(page_url, max_links=1000)
                for l in links:
                    if l not in seen:
                        seen.add(l)
                        collected.append(l)
                        if max_links and len(collected) >= max_links:
                            return collected

                # attempt to find next page link
                try:
                    r = requests.get(page_url, headers=headers, timeout=12)
                    r.raise_for_status()
                    html = r.content.decode('utf-8', errors='ignore')
                    # rel=next
                    m = re.search(r'<link[^>]+rel=["\']next["\'][^>]*href=["\'](.*?)["\']', html, flags=re.I)
                    next_url = None
                    if m:
                        next_url = urljoin(page_url, m.group(1).strip())
                    else:
                        # common pagination anchors
                        m2 = re.search(r'<a[^>]+href=["\'](.*?)["\'][^>]*>(?:\s*next\s*|»|›)</a>', html, flags=re.I)
                        if m2:
                            next_url = urljoin(page_url, m2.group(1).strip())
                        else:
                            # look for pagination with page numbers and 'next' class
                            m3 = re.search(r'<a[^>]+class=["\'][^"\']*(?:next|pager-next)[^"\']*["\'][^>]*href=["\'](.*?)["\']', html, flags=re.I)
                            if m3:
                                next_url = urljoin(page_url, m3.group(1).strip())

                    if next_url and next_url not in seen and next_url not in to_visit:
                        to_visit.append(next_url)
                except Exception:
                    pass

            except Exception:
                continue

        return collected

    # ==============================================
    # METODE DE EXTRAGERE SELENIUMBASE - COMPLETE
    # ==============================================
    
    def _extract_name_selenium(self, sb) -> str:
        """Extrage numele produsului folosind SeleniumBase"""
        selectors = [
            'h1.product-title', 
            'h1[data-testid="product-title"]',
            'h1', 
            '.product-name h1', 
            '.title',
            '.product-head h1'
        ]
        
        for selector in selectors:
            try:
                element = sb.find_element(selector)
                if element and element.text.strip():
                    return element.text.strip()
            except Exception:
                continue
        
        # Fallback la titlul paginii
        try:
            title = sb.get_title()
            if title:
                clean_title = title.split('|')[0].split('-')[0].strip()
                if clean_title and clean_title.lower() != 'darwin':
                    return clean_title
        except Exception:
            pass
        
        return "Produs Necunoscut"
    
    def _extract_description_selenium(self, sb) -> str:
        """Extrage descrierea folosind SeleniumBase"""
        selectors = [
            '.product-description', 
            '.description', 
            '.product-details',
            '.product-info',
            '.specifications',
            '.features'
        ]
        
        for selector in selectors:
            try:
                element = sb.find_element(selector)
                if element and element.text.strip():
                    desc = element.text.strip()
                    return desc[:500] + "..." if len(desc) > 500 else desc
            except Exception:
                continue
        
        return "Nu există descriere disponibilă"
    
    def _extract_price_selenium(self, sb) -> str:
        """Extrage prețul folosind SeleniumBase"""
        selectors = [
            '.price-current', 
            '.price', 
            '.product-price',
            '.sale-price',
            '.final-price'
        ]
        
        for selector in selectors:
            try:
                elements = sb.find_elements(selector)
                for element in elements:
                    text = element.text.strip()
                    price_match = re.search(r'(\d+[.,]?\d*)\s*(lei|mdl)', text.lower())
                    if price_match:
                        price_num = price_match.group(1).replace(',', '.')
                        return f"{price_num} MDL"
                    
                    number_match = re.search(r'(\d+[.,]?\d*)', text)
                    if number_match and len(text) < 20:
                        price_num = number_match.group(1).replace(',', '.')
                        return f"{price_num} MDL"
            except Exception:
                continue
        
        return "Preț indisponibil"
        # Fallback: inspect whole page text
        try:
            page_text = ''
            try:
                page_text = sb.get_text()
            except Exception:
                try:
                    page_text = sb.get_page_source()
                except Exception:
                    page_text = ''

            m = re.search(r"(\d+[\.,]?\d*)\s*(lei|mdl|ron|eur|€|usd|\$)", page_text.lower())
            if m:
                number = m.group(1).replace(',', '.')
                cur = m.group(2).upper()
                if cur in ('LEI', 'MDL'):
                    cur = 'MDL'
                elif cur in ('EUR', '€'):
                    cur = 'EUR'
                elif cur in ('USD', '$'):
                    cur = 'USD'
                return f"{number} {cur}"
        except Exception:
            pass

        return "Preț indisponibil"
    
    def _extract_category_selenium(self, sb) -> str:
        """Extrage categoria folosind SeleniumBase"""
        try:
            breadcrumbs = sb.find_elements('.breadcrumb a, .breadcrumbs a')
            if breadcrumbs and len(breadcrumbs) > 1:
                for elem in reversed(breadcrumbs):
                    text = elem.text.strip()
                    if text.lower() not in ['home', 'acasa', 'darwin', 'index']:
                        return text
        except Exception:
            pass
        
        # Fallback din URL
        try:
            current_url = sb.get_current_url()
            url_parts = current_url.split('/')
            for part in url_parts:
                if part and not part.isdigit():
                    clean_part = part.replace('-', ' ').replace('_', ' ').title()
                    if len(clean_part) > 3:
                        return clean_part
        except Exception:
            pass
        
        return "Electronice"
    
    def _extract_image_selenium(self, sb) -> str:
        """Extrage imaginea folosind SeleniumBase"""
        selectors = [
            '.product-image img', 
            '.main-image img',
            '.product-photo img',
            '.product-gallery img'
        ]
        
        for selector in selectors:
            try:
                element = sb.find_element(selector)
                if element:
                    src = element.get_attribute('src') or element.get_attribute('data-src')
                    if src and not src.endswith('.svg'):
                        # Fă URL-ul absolut
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = urljoin(sb.get_current_url(), src)
                        return src
            except Exception:
                continue
        
        return ""
    
    def _extract_availability_selenium(self, sb) -> str:
        """Extrage disponibilitatea folosind SeleniumBase"""
        selectors = [
            '.availability', 
            '.stock-status',
            '.in-stock',
            '.out-of-stock'
        ]
        
        for selector in selectors:
            try:
                element = sb.find_element(selector)
                if element and element.text.strip():
                    status = element.text.strip()
                    if any(word in status.lower() for word in ['disponibil', 'in stoc', 'pe stoc']):
                        return "În stoc"
                    elif any(word in status.lower() for word in ['indisponibil', 'lipsa', 'epuizat']):
                        return "Indisponibil"
                    else:
                        return status
            except Exception:
                continue
        
        return "Necunoscut"

    # ==============================================
    # METODE DE EXTRAGERE BEAUTIFULSOUP - COMPLETE
    # ==============================================
    
    def _extract_name_soup(self, soup) -> str:
        """Extrage numele folosind BeautifulSoup"""
        selectors = [
            'h1.product-title', 
            'h1[data-testid="product-title"]',
            'h1', 
            '.product-name h1',
            '.product-head h1'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    return element.get_text().strip()
            except Exception:
                continue
        
        # Fallback la titlul paginii
        try:
            title = soup.find('title')
            if title:
                clean_title = title.get_text().split('|')[0].split('-')[0].strip()
                if clean_title and clean_title.lower() != 'darwin':
                    return clean_title
        except Exception:
            pass
        
        return "Produs Necunoscut"
    
    def _extract_description_soup(self, soup) -> str:
        """Extrage descrierea folosind BeautifulSoup"""
        selectors = [
            '.product-description', 
            '.description', 
            '.product-details',
            '.product-info',
            '.specifications'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    desc = element.get_text().strip()
                    return desc[:500] + "..." if len(desc) > 500 else desc
            except Exception:
                continue
        
        return "Nu există descriere disponibilă"
    
    def _extract_price_soup(self, soup) -> str:
        """Extrage prețul folosind BeautifulSoup"""
        selectors = [
            '.price-current', 
            '.price', 
            '.product-price',
            '.sale-price',
            '.final-price'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    price_match = re.search(r'(\d+[.,]?\d*)\s*(lei|mdl)', text.lower())
                    if price_match:
                        price_num = price_match.group(1).replace(',', '.')
                        return f"{price_num} MDL"
                    
                    number_match = re.search(r'(\d+[.,]?\d*)', text)
                    if number_match and len(text) < 20:
                        price_num = number_match.group(1).replace(',', '.')
                        return f"{price_num} MDL"
            except Exception:
                continue
        
        return "Preț indisponibil"
        # Fallback: search full page text for currency patterns
        try:
            text = soup.get_text(separator=' ', strip=True).lower()
            m = re.search(r"(\d+[\.,]?\d*)\s*(lei|mdl|ron|eur|€|usd|\$)", text)
            if m:
                number = m.group(1).replace(',', '.')
                cur = m.group(2).upper()
                if cur in ('LEI', 'MDL'):
                    cur = 'MDL'
                elif cur in ('EUR', '€'):
                    cur = 'EUR'
                elif cur in ('USD', '$'):
                    cur = 'USD'
                return f"{number} {cur}"
        except Exception:
            pass

        return "Preț indisponibil"
    
    def _extract_category_soup(self, soup) -> str:
        """Extrage categoria folosind BeautifulSoup"""
        try:
            breadcrumbs = soup.select('.breadcrumb a, .breadcrumbs a')
            if breadcrumbs and len(breadcrumbs) > 1:
                for elem in reversed(breadcrumbs):
                    text = elem.get_text().strip()
                    if text.lower() not in ['home', 'acasa', 'darwin', 'index']:
                        return text
        except Exception:
            pass
        
        return "Electronice"
    
    def _extract_image_soup(self, soup, base_url: str) -> str:
        """Extrage imaginea folosind BeautifulSoup"""
        selectors = [
            '.product-image img', 
            '.main-image img',
            '.product-photo img'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get('src'):
                    src = element.get('src')
                    if not src.endswith('.svg'):
                        return urljoin(base_url, src)
            except Exception:
                continue
        
        return ""
    
    def _extract_availability_soup(self, soup) -> str:
        """Extrage disponibilitatea folosind BeautifulSoup"""
        selectors = [
            '.availability', 
            '.stock-status',
            '.in-stock',
            '.out-of-stock'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    status = element.get_text().strip()
                    if any(word in status.lower() for word in ['disponibil', 'in stoc', 'pe stoc']):
                        return "În stoc"
                    elif any(word in status.lower() for word in ['indisponibil', 'lipsa', 'epuizat']):
                        return "Indisponibil"
                    else:
                        return status
            except Exception:
                continue
        
        return "Necunoscut"

    def _extract_last_updated_soup(self, soup, headers: Optional[Dict[str, str]] = None) -> str:
        """Try to extract a 'last updated' timestamp from meta tags or <time> elements."""
        try:
            # common meta tags
            metas = [
                ('meta', {'property': 'article:modified_time'}),
                ('meta', {'name': 'last-modified'}),
                ('meta', {'property': 'og:updated_time'}),
                ('meta', {'name': 'updated'}),
            ]
            for tag, attrs in metas:
                el = soup.find(tag, attrs=attrs)
                if el:
                    val = el.get('content') or el.get('value')
                    if val:
                        return val.strip()

            # time elements
            time_el = soup.find('time')
            if time_el:
                dt = time_el.get('datetime') or time_el.get_text()
                if dt:
                    return dt.strip()

            # JSON-LD check
            for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', str(soup), flags=re.S | re.I):
                try:
                    jd = json.loads(m.group(1).strip())
                    if isinstance(jd, dict):
                        for key in ('dateModified', 'datePublished', 'lastReviewed'):
                            if jd.get(key):
                                return str(jd.get(key))
                except Exception:
                    continue

            # fallback to headers
            if headers:
                lm = headers.get('Last-Modified') or headers.get('last-modified')
                if lm:
                    return lm
        except Exception:
            pass
        return ""

    def _normalize_in_stock(self, availability_text: str) -> bool:
        """Return True if availability text indicates in-stock, else False."""
        if not availability_text:
            return False
        t = availability_text.lower()
        positive = ['in stoc', 'în stoc', 'disponibil', 'availability', 'available', 'in stock']
        negative = ['indisponibil', 'lipsa', 'epuizat', 'out of stock', 'unavailable', 'stoc epuizat']
        if any(p in t for p in positive) and not any(n in t for n in negative):
            return True
        return False

    def _quick_is_product_page(self, url: str, html: Optional[str] = None, timeout: int = 8) -> Dict[str, Any]:
        """Fast heuristic to decide if a page is likely a single product page.

        This uses a lightweight requests fetch (if html not provided) and
        checks for JSON-LD Product/Offers, price patterns, 'buy' buttons,
        and presence of a single H1 + price. Returns a dict with score and
        reasons to make decisions transparent.
        """
        reasons = []
        score = 0.0

        try:
            text = html
            if not text:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                r = requests.get(url, headers=headers, timeout=timeout)
                r.raise_for_status()
                text = r.content.decode('utf-8', errors='ignore')

            # Quick JSON-LD check for Product/Offer
            for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, flags=re.S | re.I):
                try:
                    jd = json.loads(m.group(1).strip())
                    # if list, flatten
                    candidates = jd if isinstance(jd, list) else [jd]
                    for entry in candidates:
                        if not isinstance(entry, dict):
                            continue
                        t = entry.get('@type') or entry.get('type') or entry.get('@context')
                        if t and ('Product' in str(t) or 'product' in str(t)):
                            score += 0.6
                            reasons.append('jsonld_product')
                        if entry.get('offers'):
                            score += 0.4
                            reasons.append('jsonld_offers')
                except Exception:
                    continue

            # Meta og:type
            if re.search(r'<meta[^>]+property=["\']og:type["\'][^>]*content=["\']product["\']', text, flags=re.I):
                score += 0.3
                reasons.append('og:type=product')

            # Price patterns
            if re.search(r"\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d+)?\s*(lei|mdl|ron|€|eur|usd|\$)", text, flags=re.I):
                score += 0.6
                reasons.append('price_pattern')

            # 'Buy' / add-to-cart buttons
            if re.search(r'(adauga in cos|adaugă în coș|cumpără|buy now|add to cart|add-to-cart|cart)', text, flags=re.I):
                score += 0.4
                reasons.append('buy_button')

            # Single H1 presence
            h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', text, flags=re.S | re.I)
            if h1s and len(h1s) == 1:
                score += 0.2
                reasons.append('single_h1')
            elif h1s and len(h1s) > 1:
                reasons.append('multiple_h1')

            # If page contains many product cards (likely listing), penalize
            # look for repeated product-card classes or many .product-card occurrences
            repeats = len(re.findall(r'(product-card|product-item|product-listing|product__card)', text, flags=re.I))
            if repeats >= 3:
                score -= 0.6
                reasons.append('many_cards')

            # Extract product specification-like features (brand, model, id, dimensions, resolutie, connectivity)
            spec_info = self._extract_spec_features(text)
            if spec_info.get('count', 0) >= 3:
                score += 0.6
                reasons.append('product_specs')
            elif spec_info.get('count', 0) >= 1:
                score += 0.2
                reasons.append('partial_specs')

            # Detect service / insurance / informational pages and penalize strongly
            service_keywords = [
                r'\basigurare\b', r'\bpoli[țt]a\b', r'\basigurari\b', r'\bpolita\b', r'\basigurator',
                r'\bservicii\b', r'\babonament\b', r'\bcalatorie', r'\bvacan', r'\bconsultant', r'\bFAQ\b', r'\bîntrebari frecvente\b'
            ]
            service_found = False
            for sk in service_keywords:
                if re.search(sk, text, flags=re.I):
                    service_found = True
                    reasons.append('service_keyword')
                    break

            # If service-like content is detected, require stronger spec evidence to mark as product
            if service_found:
                # if many concrete specs present then still allow, else strongly penalize
                if spec_info.get('count', 0) < 4:
                    score -= 0.9
                    reasons.append('penalize_service')

            # Normalize score to 0..1
            score = max(0.0, min(1.0, score))

            # Compute stricter acceptance rules
            has_jsonld_product = any(r in reasons for r in ('jsonld_product',))
            has_jsonld_offers = any(r in reasons for r in ('jsonld_offers',))
            spec_count = spec_info.get('count', 0)

            # detect price and brand/model/product id presence
            has_price = 'price_pattern' in reasons or 'price' in spec_info.get('found', [])
            found = set(spec_info.get('found', []))
            has_brand = 'brand' in found
            has_model = 'model' in found or 'model_number' in found
            has_product_id = 'product_id' in found

            # Strong negative: service_found with low spec evidence already penalized above

            # Acceptance: JSON-LD product OR spec_count >= 3 OR (has_price AND (brand OR model OR product_id))
            is_product_rule = False
            if has_jsonld_product or has_jsonld_offers:
                is_product_rule = True
                reasons.append('rule_jsonld')
            elif spec_count >= 3:
                is_product_rule = True
                reasons.append('rule_spec_count')
            elif has_price and (has_brand or has_model or has_product_id):
                is_product_rule = True
                reasons.append('rule_price_plus_spec')

            # Fallback: if score high enough and not service penalized
            is_product_fallback = (score >= 0.7) and (not any('penalize_service' in r for r in [reasons]))

            is_product = bool(is_product_rule) or bool(is_product_fallback)

            out = {"url": url, "is_product": is_product, "score": score, "reasons": reasons}
            out['specs_found'] = spec_info.get('found', [])
            out['spec_count'] = spec_count
            return out

        except Exception as e:
            return {"url": url, "is_product": False, "score": 0.0, "reasons": [f"error:{str(e)}"]}

    def _extract_spec_features(self, text: str) -> Dict[str, Any]:
        """Parse page text for structured product-spec-like characteristics.

        Returns dict with 'found' list and 'count'. This is a lightweight
        heuristic that looks for common spec labels and value patterns.
        """
        found = set()
        try:
            # common labels in Romanian / English / Russian
            label_patterns = {
                'brand': r'\b(Brand|Producator|Producător|Brand:)\b',
                'model': r'\b(Model|Model:|Modelul)\b',
                'product_id': r'\b(ID produs|ID produs:|ID:|SKU:|Produs ID|ID produs)\b',
                'dimensions': r'\b(Dimensiuni|Dimensiuni:|mm|cm|x\s*mm|x\s*cm)\b',
                'weight': r'\b(Greutate|Greutate:)\b',
                'resolution': r'\b(Full\s*HD|1920\s*x\s*1080|4K|3840\s*x\s*2160|Rezoluție|Rezolutie)\b',
                'refresh': r'\b(Hz|Refresh rate|Reîmprospătare|60 Hz|144 Hz)\b',
                'connectivity': r'\b(HDMI|DVI|VGA|DisplayPort|USB-C|USB)\b',
                'response_time': r'\b(Timpul de răspuns|ms|ms)\b',
                'colors': r'\b(16\.7 Million|numărul de culori|culori)\b'
            }

            for name, pat in label_patterns.items():
                if re.search(pat, text, flags=re.I):
                    found.add(name)

            # also try to detect explicit model numbers like '273V7QDSB' or sequences with letters+digits
            if re.search(r'\b[A-Za-z]+[-_]?[0-9]{2,}[A-Za-z0-9-]*\b', text):
                found.add('model_number')

            # price numeric presence counts as a spec indicator too
            if re.search(r"\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d+)?\s*(lei|mdl|ron|€|eur|usd|\$)", text, flags=re.I):
                found.add('price')

            return {'found': sorted(list(found)), 'count': len(found)}
        except Exception:
            return {'found': [], 'count': 0}

    def classify_page_product_count(self, page_url: str, html: Optional[str] = None, max_chars: int = 30000) -> Dict[str, Any]:
        """Uses the configured OpenAI model to classify whether a page represents
        a single product page or multiple products/variants.

        Returns a dict with at least: {"type": "single"|"multiple"|"unknown", "confidence": float, "reason": str, "raw": str}
        """
        try:
            if not html:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                r = requests.get(page_url, headers=headers, timeout=12)
                r.raise_for_status()
                html = r.content.decode('utf-8', errors='ignore')

            # Truncate very long pages to avoid hitting model limits
            snippet = html[:max_chars]

            prompt = (
                "Ești un clasificator. Primești conținut HTML al unei pagini din darwin.md.\n"
                "Răspunde strict în JSON cu cheile: type, confidence, reason.\n"
                "- type: 'single' dacă pagina prezintă un singur produs (pagina de detaliu) sau 'multiple' dacă este o pagină de listare/variantă cu mai multe produse/legături către produse.\n"
                "- confidence: un număr între 0 și 1 care indică încrederea ta.\n"
                "- reason: motivul deciziei, 1-2 propoziții în română.\n"
                "DOAR returnează obiectul JSON, nimic altceva.\n\n"
                "Exemple:\n"
                "Pagina de produs (așteptare) -> {\"type\": \"single\", \"confidence\": 0.95, \"reason\": \"Pagina are un singur H1 de produs, elemente de preț și descriere\"}\n"
                "Pagina de listare (așteptare) -> {\"type\": \"multiple\", \"confidence\": 0.98, \"reason\": \"Mulți linkuri de produs, carduri repetate cu imagini și prețuri\"}\n\n"
            )

            # Provide a short context plus the HTML snippet
            full_prompt = prompt + "\nCONȚINUT_HTML:\n" + snippet

            # Try a few common method names on the model adapter
            response_text = None
            model = getattr(self, 'model', None)
            if not model:
                return {"type": "unknown", "confidence": 0.0, "reason": "Model OpenAI neconfigurat", "raw": ""}

            candidate_methods = ['chat', 'create', 'complete', 'predict', 'generate']
            for mname in candidate_methods:
                fn = getattr(model, mname, None)
                if not fn:
                    continue
                try:
                    # attempt calling patterns
                    if mname == 'chat':
                        # many adapters accept a messages list
                        resp = fn([{"role": "user", "content": full_prompt}], temperature=0.0)
                    else:
                        try:
                            resp = fn(full_prompt, temperature=0.0)
                        except TypeError:
                            resp = fn(full_prompt)

                    # Extract text from common response shapes
                    if isinstance(resp, str):
                        response_text = resp
                    elif isinstance(resp, dict):
                        # OpenAI-like response
                        if 'content' in resp:
                            response_text = resp['content']
                        elif 'text' in resp:
                            response_text = resp['text']
                        elif 'choices' in resp and isinstance(resp['choices'], list) and len(resp['choices'])>0:
                            ch = resp['choices'][0]
                            if isinstance(ch, dict):
                                response_text = ch.get('message', {}).get('content') or ch.get('text') or json.dumps(ch)
                            else:
                                response_text = str(ch)
                    else:
                        response_text = str(resp)

                    if response_text:
                        break
                except Exception:
                    # try next method
                    continue

            if not response_text:
                return {"type": "unknown", "confidence": 0.0, "reason": "Model call failed or returned no text", "raw": ""}

            # Try to parse JSON substring from the response
            j = None
            try:
                # find first JSON object in the text
                m = re.search(r"\{[\s\S]*\}", response_text)
                if m:
                    j = json.loads(m.group(0))
                else:
                    # last attempt: parse entire string
                    j = json.loads(response_text)
            except Exception:
                # fallback: simple heuristics
                low = response_text.lower()
                if 'multiple' in low or 'list' in low or 'mai multe' in low or 'card' in low:
                    return {"type": "multiple", "confidence": 0.6, "reason": "Detecție heuristica din text model: conține indicații de listare", "raw": response_text}
                if 'single' in low or 'produs' in low and 'h1' in low:
                    return {"type": "single", "confidence": 0.6, "reason": "Detecție heuristica: model a menționat 'produs'", "raw": response_text}

                return {"type": "unknown", "confidence": 0.0, "reason": "Răspuns model neinterpretabil", "raw": response_text}

            # Normalize fields
            result_type = j.get('type') if isinstance(j.get('type'), str) else None
            confidence = float(j.get('confidence') or 0.0)
            reason = j.get('reason') or ''

            if result_type not in ('single', 'multiple'):
                # try to infer
                rt = str(result_type).lower() if result_type else ''
                if 'single' in rt or 'produs' in rt:
                    result_type = 'single'
                elif 'multiple' in rt or 'list' in rt or 'mai multe' in rt:
                    result_type = 'multiple'
                else:
                    result_type = 'unknown'

            return {"type": result_type, "confidence": confidence, "reason": reason, "raw": response_text}

        except Exception as e:
            logging.exception("Eroare la clasificarea paginii cu OpenAI")
            return {"type": "unknown", "confidence": 0.0, "reason": str(e), "raw": ""}

    def sitemap_index_summary(self, sitemap_url: str = "https://darwin.md/sitemap.xml", sample_per_sub: int = 5, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Fetches a sitemap index (or sitemap) and returns a JSON-serializable
        summary describing subsitemaps, their types and a small sample of URLs
        from each. Also writes the summary to a JSON file if output_file is provided
        or generates a timestamped file name.

        Returns a dict with keys: sitemap_url, subsitemaps (list), fetched_at.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r = requests.get(sitemap_url, headers=headers, timeout=20)
            r.raise_for_status()
            content = r.content.decode('utf-8', errors='ignore')

            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            try:
                root = ET.fromstring(content)
            except Exception:
                # not valid XML
                return {"success": False, "error": "Sitemap-ul nu este XML valid", "sitemap_url": sitemap_url}

            subs = []

            # If sitemap index
            sitemap_entries = root.findall('.//ns:sitemap', namespace)
            if sitemap_entries:
                for s in sitemap_entries:
                    loc = s.find('ns:loc', namespace)
                    lastmod = s.find('ns:lastmod', namespace)
                    if loc is None or not loc.text:
                        continue
                    sub_url = loc.text.strip()
                    sub_info = {"loc": sub_url, "lastmod": (lastmod.text.strip() if lastmod is not None and lastmod.text else None)}

                    # try to fetch a small sample from subsitemap
                    try:
                        r2 = requests.get(sub_url, headers=headers, timeout=15)
                        r2.raise_for_status()
                        sub_text = r2.content.decode('utf-8', errors='ignore')
                        try:
                            subroot = ET.fromstring(sub_text)
                            url_elems = subroot.findall('.//ns:url', namespace)
                            total = len(url_elems)
                            samples = []
                            for ue in url_elems[:sample_per_sub]:
                                l = ue.find('ns:loc', namespace)
                                lm = ue.find('ns:lastmod', namespace)
                                if l is not None and l.text:
                                    samples.append({"loc": l.text.strip(), "lastmod": (lm.text.strip() if lm is not None and lm.text else None)})
                            sub_info.update({"type": "urlset", "total_urls": total, "sample_urls": samples})
                        except Exception:
                            # not a urlset - store raw info
                            sub_info.update({"type": "unknown", "total_urls": None, "sample_urls": []})
                    except Exception:
                        sub_info.update({"type": "unreachable", "total_urls": None, "sample_urls": []})

                    subs.append(sub_info)
            else:
                # sitemap is a urlset directly
                url_elements = root.findall('.//ns:url', namespace)
                total = len(url_elements)
                samples = []
                for ue in url_elements[:sample_per_sub]:
                    loc = ue.find('ns:loc', namespace)
                    lm = ue.find('ns:lastmod', namespace)
                    if loc is not None and loc.text:
                        samples.append({"loc": loc.text.strip(), "lastmod": (lm.text.strip() if lm is not None and lm.text else None)})
                subs.append({"loc": sitemap_url, "type": "urlset", "total_urls": total, "sample_urls": samples})

            result = {
                "success": True,
                "sitemap_url": sitemap_url,
                "fetched_at": datetime.utcnow().isoformat() + 'Z',
                "subsitemaps": subs
            }

            # write to file
            if not output_file:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f'sitemap_summary_{ts}.json'

            try:
                with open(output_file, 'w', encoding='utf-8') as jf:
                    json.dump(result, jf, ensure_ascii=False, indent=2)
                logging.info(f"Sitemap summary scris în: {output_file}")
                result['output_file'] = output_file
            except Exception as e:
                logging.warning(f"Nu am putut scrie fișierul JSON: {str(e)}")

            return result

        except Exception as e:
            logging.exception('Eroare la sumarizarea sitemap-ului')
            return {"success": False, "error": str(e), "sitemap_url": sitemap_url}

    @tool(description="Validează și curăță datele extrase despre produse")
    def validate_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validează și curăță datele extrase despre produse pentru asigurarea calității
        
        Args:
            product: Dicționar cu datele brute despre produs
            
        Returns:
            Date despre produs curate și validate
        """
        if product.get("error"):
            return product
        
        # Curăță și validează numele
        name = product.get("name", "").strip()
        if not name or name == "Produs Necunoscut":
            try:
                name = "Produs " + product.get("url", "").split("/")[-1]
            except Exception:
                name = "Produs Necunoscut"
        
        # Curăță și validează prețul
        price = self._clean_price(product.get("price", ""))
        
        # Curăță descrierea
        description = product.get("description", "").strip()
        if len(description) > 500:
            description = description[:497] + "..."
        
        # Validează și curăță categoria
        category = self._clean_category(product.get("category", ""))
        
        # Validează URL-ul imaginii
        image_url = product.get("image_url", "")
        if image_url and not image_url.startswith("http"):
            image_url = ""
        
        return {
            "name": name,
            "description": description if description else "Nu există descriere disponibilă",
            "price": price,
            "category": category,
            "url": product.get("url", ""),
            "image_url": image_url,
            "availability": product.get("availability", "Necunoscut"),
            "last_updated": product.get("last_updated", ""),
            "in_stock": bool(product.get("in_stock", False)),
            "extraction_method": product.get("extraction_method", "unknown"),
            "is_valid": self._is_valid_product(name, price)
        }

    def validate_product_data_raw(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Call the underlying validate implementation avoiding decorator wrappers.
        This mirrors discover_all_products_raw pattern for safety when the
        decorated method is not directly callable.
        """
        # Try instance attribute first
        try:
            inst_attr = getattr(self, 'validate_product_data', None)
            if callable(inst_attr):
                try:
                    return inst_attr(product)
                except TypeError:
                    try:
                        return inst_attr()
                    except Exception:
                        pass
        except Exception:
            pass

        # Fallback to raw function in class dict
        raw = self.__class__.__dict__.get('validate_product_data')
        if raw:
            try:
                return raw(self, product)
            except Exception:
                # try unwrapping common attributes
                for attr in ('__wrapped__', 'func', 'fn', 'function'):
                    inner = getattr(raw, attr, None)
                    if inner:
                        try:
                            return inner(self, product)
                        except Exception:
                            continue

        # As a last resort, call the implementation logic directly if present
        try:
            return {
                "name": product.get("name", "Produs Necunoscut"),
                "description": product.get("description", ""),
                "price": self._clean_price(product.get("price", "")),
                "category": self._clean_category(product.get("category", "")),
                "url": product.get("url", ""),
                "image_url": product.get("image_url", ""),
                "availability": product.get("availability", "Necunoscut"),
                "last_updated": product.get("last_updated", ""),
                "in_stock": bool(product.get("in_stock", False)),
                "extraction_method": product.get("extraction_method", "unknown"),
                "is_valid": self._is_valid_product(product.get("name", ""), self._clean_price(product.get("price", "")))
            }
        except Exception:
            return product
    
    def _clean_price(self, price_text: str) -> str:
        """Curăță și standardizează formatul prețului - îmbunătățit pentru toate formatele"""
        if not price_text or "indisponibil" in price_text.lower():
            return "0 MDL"
        
        # Mapare monede
        currency_mapping = {
            'lei': 'MDL',
            'mdl': 'MDL',
            'eur': 'EUR',
            'euro': 'EUR',
            'usd': 'USD',
            'dollar': 'USD',
            '$': 'USD',
            '€': 'EUR'
        }
        
        # Extrage valoarea numerică și moneda
        price_match = re.search(r'(\d+[.,]?\d*)\s*([a-zA-Z$€]+)?', price_text)
        if price_match:
            number = price_match.group(1).replace(',', '.')
            currency = price_match.group(2) or 'mdl'
            
            try:
                # Verifică dacă este un număr valid
                float(number)
                # Mapează moneda
                currency_clean = currency_mapping.get(currency.lower(), 'MDL')
                return f"{number} {currency_clean}"
            except ValueError:
                pass
        
        return "0 MDL"
    
    def _clean_category(self, category: str) -> str:
        """Curăță și standardizează numele categoriilor"""
        if not category or category == "Electronice":
            return "General"
        
        # Standardizează categoriile Darwin
        category_mapping = {
            "telefoane": "Telefoane",
            "smartphone": "Smartphone-uri",
            "telefoane mobile cu buton": "Telefoane cu Buton",
            "telefoane dect": "Telefoane DECT",
            "laptopuri": "Laptopuri", 
            "tablete": "Tablete",
            "accesorii": "Accesorii",
            "audio": "Audio",
            "casti": "Căști",
            "boxe": "Boxe",
            "gaming": "Gaming",
            "smart home": "Smart Home",
            "monitoare": "Monitoare",
            "sisteme pc": "Sisteme PC",
            "componente pc": "Componente PC",
            "periferice pc": "Periferice PC",
            "imprimante": "Imprimante",
            "camere foto": "Camere Foto",
            "camere action": "Camere Action",
            "camere supraveghere": "Camere Supraveghere",
            "tehnica bucatarie": "Electronice Bucătărie",
            "aspiratoare": "Aspiratoare",
            "aparate fitness": "Aparate Fitness",
            "transport personal": "Transport Personal",
            "drone": "Drone",
            "ochelari vr": "Ochelari VR",
            "ceasuri inteligente": "Ceasuri Inteligente",
            "bratari inteligente": "Brățări Inteligente"
        }
        
        category_lower = category.lower().strip()
        for key, value in category_mapping.items():
            if key in category_lower:
                return value
        
        return category.title()
    
    def _is_valid_product(self, name: str, price: str) -> bool:
        """Verifică dacă datele produsului sunt valide pentru export - îmbunătățit"""
        # Validări de bază
        if not name or name == "Produs Necunoscut" or len(name) < 3:
            return False
        
        if not price or price == "0 MDL" or "indisponibil" in price.lower():
            return False
        
        # Verificări suplimentare
        # Exclude produsele cu nume prea generice
        generic_names = ['produs', 'item', 'article', 'product']
        if any(generic.lower() in name.lower() for generic in generic_names):
            return len(name) > 15  # Acceptă doar dacă are și alte detalii
        
        return True
    
    @tool(description="Analizează categoriile și structura produselor Darwin.md")
    def analyze_darwin_categories(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analizează produsele extrase pentru a înțelege structura categoriilor Darwin.md
        
        Args:
            products: Lista de date extrase despre produse
            
        Returns:
            Analiză de categorii și distribuție produse
        """
        if not products:
            return {
                "total_products": 0,
                "valid_products": 0,
                "invalid_products": 0,
                "categories": {},
                "category_count": 0,
                "quality_score": 0,
                "most_popular_category": "N/A"
            }
        
        category_stats = {}
        valid_products = 0
        total_products = len(products)
        
        for product in products:
            if product.get("is_valid"):
                valid_products += 1
                category = product.get("category", "Necunoscut")
                
                if category not in category_stats:
                    category_stats[category] = {
                        "count": 0,
                        "avg_price": 0,
                        "min_price": float('inf'),
                        "max_price": 0,
                        "products": []
                    }
                
                category_stats[category]["count"] += 1
                category_stats[category]["products"].append(product)
                
                # Calculează statistici preț
                price_text = product.get("price", "0 MDL")
                price_match = re.search(r'(\d+[.,]?\d*)', price_text)
                if price_match:
                    try:
                        price_value = float(price_match.group(1).replace(',', '.'))
                        current_avg = category_stats[category]["avg_price"]
                        current_count = category_stats[category]["count"]
                        category_stats[category]["avg_price"] = (
                            (current_avg * (current_count - 1) + price_value) / current_count
                        )
                        
                        # Min/Max preț
                        if price_value < category_stats[category]["min_price"]:
                            category_stats[category]["min_price"] = price_value
                        if price_value > category_stats[category]["max_price"]:
                            category_stats[category]["max_price"] = price_value
                    except ValueError:
                        pass
        
        # Curăță valorile infinite
        for category in category_stats:
            if category_stats[category]["min_price"] == float('inf'):
                category_stats[category]["min_price"] = 0
        
        # Determină categoria cea mai populară
        most_popular = "N/A"
        if category_stats:
            most_popular = max(category_stats.items(), key=lambda x: x[1]["count"])[0]
        
        return {
            "total_products": total_products,
            "valid_products": valid_products,
            "invalid_products": total_products - valid_products,
            "categories": category_stats,
            "category_count": len(category_stats),
            "quality_score": (valid_products / total_products * 100) if total_products > 0 else 0,
            "most_popular_category": most_popular
        }
    
    def export_to_csv(self, products: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Exportă produsele în format CSV pentru Telegram Bot + ChromaDB
        
        Args:
            products: Lista de date validate despre produse
            filename: Nume fișier personalizat (opțional)
            
        Returns:
            Calea către fișierul CSV exportat
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"darwin_products_{timestamp}.csv"
        
        # Pregătește datele pentru CSV
        csv_data = []
        for i, product in enumerate(products):
            if product.get("is_valid"):
                csv_data.append({
                    "id": f"darwin_{i+1:04d}",
                    "name": product.get("name", ""),
                    "description": product.get("description", ""),
                    "price": product.get("price", ""),
                    "category": product.get("category", ""),
                    "url": product.get("url", ""),
                    "image_url": product.get("image_url", ""),
                    "availability": product.get("availability", ""),
                    "last_updated": product.get("last_updated", ""),
                    "in_stock": bool(product.get("in_stock", False)),
                    "extraction_method": product.get("extraction_method", "")
                })
        
        # Scrie în CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["id", "name", "description", "price", "category", "url", "image_url", "availability", "last_updated", "in_stock", "extraction_method"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            logging.info(f"CSV exportat cu succes: {filename} ({len(csv_data)} produse)")
            return filename
            
        except Exception as e:
            logging.error(f"Eroare la exportul CSV: {str(e)}")
            raise e
    
    def export_to_json(self, products: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Exportă produsele în format JSON pentru procesare ulterioară
        
        Args:
            products: Lista de date validate despre produse
            filename: Nume fișier personalizat (opțional)
            
        Returns:
            Calea către fișierul JSON exportat
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"darwin_products_{timestamp}.json"
        
        # Filtrează doar produsele valide
        valid_products = [product for product in products if product.get("is_valid")]
        
        # Adaugă metadate
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_products": len(valid_products),
                "source": "darwin.md",
                "scraper_version": "1.0",
                "libraries_used": {
                    "drissionpage": DRISSIONPAGE_AVAILABLE,
                    "seleniumbase": SELENIUMBASE_AVAILABLE,
                    "beautifulsoup": BEAUTIFULSOUP_AVAILABLE
                }
            },
            "products": valid_products
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            
            logging.info(f"JSON exportat cu succes: {filename} ({len(valid_products)} produse)")
            return filename
            
        except Exception as e:
            logging.error(f"Eroare la exportul JSON: {str(e)}")
            raise e

    def repair_jsonl_checkpoints(self, jsonl_path: str, output_prefix: str = 'repaired_batch') -> Dict[str, Any]:
        """
        Repară și revalidatează un fișier JSONL de checkpoint-uri fără a re-fetch-ui paginile.

        - Normalizează prețurile extrăgând valoarea din `availability` sau `description` când `price` e lipsă/0.
        - Recalculează `in_stock` din `availability`.
        - Rulează `validate_product_data_raw` pentru a obține forma finală și `is_valid`.
        - Scrie fișiere: <output_prefix>.jsonl, <output_prefix>_final.json, <output_prefix>_final.csv

        Returns dict summary with counts and filenames.
        """
        repaired = []
        total = 0
        repaired_price = 0
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as jf:
                for line in jf:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    total += 1

                    orig_price = item.get('price', '') or ''
                    # If price is missing or placeholder, try to extract from availability/description
                    need_price_fix = (not orig_price) or orig_price.strip() == '' or orig_price.strip() == '0 MDL' or 'indisponibil' in str(orig_price).lower() or 'preț' in str(orig_price).lower() and 'indisponibil' in str(orig_price).lower()

                    if need_price_fix:
                        candidates = [item.get('availability', ''), item.get('description', ''), json.dumps(item, ensure_ascii=False)]
                        found = None
                        for c in candidates:
                            try:
                                p = self._extract_price_from_text(c or '')
                                if p:
                                    found = p
                                    break
                            except Exception:
                                continue
                        if found:
                            item['price'] = found
                            repaired_price += 1
                        else:
                            # keep existing cleaned placeholder
                            item['price'] = orig_price or '0 MDL'

                    # Ensure last_updated if present remains, otherwise keep empty
                    if not item.get('last_updated'):
                        item['last_updated'] = item.get('last_updated', '')

                    # Recompute in_stock from availability text
                    try:
                        item['in_stock'] = bool(self._normalize_in_stock(item.get('availability', '')))
                    except Exception:
                        item['in_stock'] = bool(item.get('in_stock', False))

                    # Run the validator to get cleaned fields and is_valid
                    try:
                        validated = self.validate_product_data_raw(item)
                    except Exception:
                        validated = item

                    repaired.append(validated)

            # Write repaired jsonl
            out_jsonl = f"{output_prefix}.jsonl"
            try:
                with open(out_jsonl, 'w', encoding='utf-8') as of:
                    for it in repaired:
                        of.write(json.dumps(it, ensure_ascii=False) + '\n')
            except Exception as e:
                logging.warning(f"Could not write repaired jsonl: {e}")

            # Final json and csv
            out_json = f"{output_prefix}_final.json"
            out_csv = f"{output_prefix}_final.csv"
            try:
                self.export_to_json(repaired, filename=out_json)
            except Exception:
                logging.warning('Final JSON export failed for repaired set')
            try:
                self.export_to_csv(repaired, filename=out_csv)
            except Exception:
                logging.warning('Final CSV export failed for repaired set')

            summary = {
                'success': True,
                'input_jsonl': jsonl_path,
                'output_jsonl': out_jsonl,
                'final_json': out_json,
                'final_csv': out_csv,
                'total_rows': total,
                'prices_repaired': repaired_price,
                'valid_products': len([p for p in repaired if p.get('is_valid')]),
                'repaired_count': len(repaired)
            }
            logging.info(f"Repair complete: {summary}")
            return summary

        except FileNotFoundError:
            return {'success': False, 'error': f'File not found: {jsonl_path}'}
        except Exception as e:
            logging.exception('Error repairing jsonl')
            return {'success': False, 'error': str(e)}

    def run_batch_local_extraction(self, urls: List[str], workers: int = 20, max_urls: Optional[int] = 1000, output_prefix: str = 'batch_local', checkpoint_every: int = 50, prefer_backend: str = 'auto') -> Dict[str, Any]:
        """
        Run a local-only batch extraction over provided URLs without using the AI agent.

        Args:
            urls: list of URLs to process
            workers: number of parallel workers
            max_urls: maximum number of urls to process from the list
            output_prefix: prefix for output files
            checkpoint_every: flush incremental results every N processed URLs

        Returns:
            summary dict with produced files and statistics
        """
        self.scraping_stats['start_time'] = datetime.now()

        if not urls:
            return {"success": False, "error": "No URLs provided"}

        if max_urls and max_urls > 0:
            urls = urls[:max_urls]

        total = len(urls)
        logging.info(f"Starting local batch extraction: {total} URLs, workers={workers}")

        results = []
        failed = []
        processed = 0

        jsonl_path = f"{output_prefix}.jsonl"
        # ensure file exists/empty
        try:
            open(jsonl_path, 'w', encoding='utf-8').close()
        except Exception:
            pass

        def worker(u):
            try:
                res = None
                # honor backend preference: 'drissionpage', 'requests', or 'auto'
                if prefer_backend == 'drissionpage' and DRISSIONPAGE_AVAILABLE:
                    try:
                        res = self._extract_with_drissionpage(u)
                        if res and not res.get('error'):
                            res['extraction_method'] = 'drissionpage'
                    except Exception as e:
                        logging.warning(f"DrissionPage extraction failed for {u}: {e}")
                        res = None

                if prefer_backend == 'requests' and BEAUTIFULSOUP_AVAILABLE and (not res or res.get('error')):
                    try:
                        res = self._extract_with_requests(u)
                        if res and not res.get('error'):
                            res['extraction_method'] = 'requests'
                    except Exception as e:
                        logging.warning(f"Requests extraction failed for {u}: {e}")
                        res = None

                # fallback to the general implementation which will try all available backends
                if not res or res.get('error'):
                    try:
                        res = self._extract_product_details_impl(u)
                    except Exception as e:
                        return {'url': u, 'error': str(e)}

                if res.get('error'):
                    return {'url': u, 'error': res.get('error')}

                validated = self.validate_product_data_raw(res)
                return validated
            except Exception as e:
                return {'url': u, 'error': str(e)}

        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(worker, u): u for u in urls}
            for fut in as_completed(future_map):
                url = future_map[fut]
                try:
                    item = fut.result()
                except Exception as e:
                    logging.warning(f"Local extraction failed for {url}: {e}")
                    failed.append(url)
                    self.failed_urls.append(url)
                    self.scraping_stats['failed_extractions'] += 1
                    continue

                processed += 1
                # record
                if item.get('error'):
                    failed.append(url)
                    self.failed_urls.append(url)
                    self.scraping_stats['failed_extractions'] += 1
                else:
                    results.append(item)
                    if item.get('is_valid'):
                        self.scraping_stats['products_extracted'] += 1

                # incremental write to jsonl every checkpoint
                if processed % checkpoint_every == 0 or processed == total:
                    try:
                        with open(jsonl_path, 'a', encoding='utf-8') as jf:
                            # append only the newest checkpoint batch
                            for r in results[-checkpoint_every:]:
                                jf.write(json.dumps(r, ensure_ascii=False) + '\n')
                        csv_name = f"{output_prefix}_{processed}.csv"
                        try:
                            self.export_to_csv(results, filename=csv_name)
                        except Exception:
                            logging.warning('Could not write checkpoint CSV')
                        logging.info(f"Checkpoint saved: {jsonl_path} (+ {len(results)} items) and {csv_name}")
                    except Exception as e:
                        logging.warning(f"Checkpoint write failed: {e}")

        # final exports
        final_json = f"{output_prefix}_final.json"
        final_csv = f"{output_prefix}_final.csv"
        try:
            self.export_to_json(results, filename=final_json)
        except Exception:
            logging.warning('Final JSON export failed')
        try:
            self.export_to_csv(results, filename=final_csv)
        except Exception:
            logging.warning('Final CSV export failed')

        self.scraping_stats['end_time'] = datetime.now()
        try:
            self.scraping_stats['duration'] = (self.scraping_stats['end_time'] - self.scraping_stats['start_time']).total_seconds()
        except Exception:
            pass

        return {
            'success': True,
            'processed': processed,
            'products_count': len(results),
            'failed_count': len(failed),
            'jsonl_checkpoint': jsonl_path,
            'final_json': final_json,
            'final_csv': final_csv,
            'statistics': self.scraping_stats
        }

    def run_full_sitemap_extraction(self, sitemap_url: str = "https://darwin.md/sitemap.xml", workers: int = 20, max_products: Optional[int] = None, output_csv: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover all product URLs from the sitemap and extract them in parallel.

        Args:
            sitemap_url: sitemap index URL
            workers: number of parallel workers
            max_products: limit number of products to process (None = all)
            output_csv: optional CSV filename

        Returns:
            dict with success, csv_file, json_file, statistics, failed_urls
        """
        self.scraping_stats['start_time'] = datetime.now()

        # Discover product URLs
        disc = self._discover_impl(sitemap_url)
        if not disc.get('success'):
            return {"success": False, "error": "Failed to discover sitemap", "details": disc}

        product_urls = disc.get('product_urls', [])
        if max_products and max_products > 0:
            product_urls = product_urls[:max_products]

        total = len(product_urls)
        logging.info(f"Starting full sitemap extraction: {total} product URLs, workers={workers}")

        results = []
        failed = []

        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_map = {ex.submit(self._extract_product_details_impl, url): url for url in product_urls}

            completed = 0
            for fut in as_completed(future_map):
                url = future_map[fut]
                try:
                    res = fut.result()
                except Exception as e:
                    logging.warning(f"Extraction task failed for {url}: {e}")
                    failed.append(url)
                    self.failed_urls.append(url)
                    self.scraping_stats['failed_extractions'] += 1
                    continue

                completed += 1
                if res.get('error'):
                    failed.append(url)
                    self.failed_urls.append(url)
                    self.scraping_stats['failed_extractions'] += 1
                else:
                    validated = self.validate_product_data_raw(res)
                    results.append(validated)
                    if validated.get('is_valid'):
                        self.scraping_stats['products_extracted'] += 1

                if completed % 100 == 0 or completed == total:
                    logging.info(f"Progress: {completed}/{total} processed; valid={len([p for p in results if p.get('is_valid')])}; failed={len(failed)}")

        # finalize
        self.scraping_stats['end_time'] = datetime.now()
        try:
            self.scraping_stats['duration'] = (self.scraping_stats['end_time'] - self.scraping_stats['start_time']).total_seconds()
        except Exception:
            pass

        csv_file = None
        json_file = None
        try:
            csv_file = self.export_to_csv(results, filename=output_csv) if output_csv else self.export_to_csv(results)
            json_file = self.export_to_json(results)
        except Exception as e:
            logging.warning(f"Export failed: {e}")

        return {
            "success": True,
            "csv_file": csv_file,
            "json_file": json_file,
            "products_count": len(results),
            "failed_count": len(failed),
            "failed_urls": failed,
            "statistics": self.scraping_stats
        }

    # ...existing code...

    def run_complete_extraction(self, max_products: int = None) -> Dict[str, Any]:
        """
        Rulează procesul complet de extragere pentru Darwin.md
        
        Args:
            max_products: Numărul maxim de produse de extras (None = toate)
            
        Returns:
            Rezultatele complete ale extragerii și statisticile
        """
        self.scraping_stats["start_time"] = datetime.now()
        
        try:
            # Pas 1: Descoperă toate URL-urile de produse
            if 'st' in globals():
                st.info("🔍 Pas 1: Descoperirea URL-urilor de produse din sitemap...")
            logging.info("Începe descoperirea URL-urilor de produse")
            
            discovery_result = self.discover_all_products()
            
            if not discovery_result.get("success"):
                return discovery_result
            
            product_urls = discovery_result["product_urls"]
            if max_products:
                product_urls = product_urls[:max_products]
                if 'st' in globals():
                    st.info(f"📋 Limitez extragerea la {max_products} produse")
                logging.info(f"Limitez extragerea la {max_products} produse")
            
            if 'st' in globals():
                st.success(f"✅ Am găsit {len(product_urls)} URL-uri de produse")
            logging.info(f"Găsite {len(product_urls)} URL-uri de produse")
            
            # Pas 2: Extrage detaliile produselor
            if 'st' in globals():
                st.info("📦 Pas 2: Extragerea detaliilor produselor...")
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            logging.info("Începe extragerea detaliilor produselor")
            
            all_products = []
            for i, url in enumerate(product_urls):
                # Actualizează progresul
                if 'st' in globals():
                    progress = (i + 1) / len(product_urls)
                    progress_bar.progress(progress)
                    status_text.text(f"Procesez {i+1}/{len(product_urls)}: {url.split('/')[-1]}")
                
                # Extrage produsul
                product_data = self.extract_product_details(url)
                
                # Validează produsul
                if not product_data.get("error"):
                    validated_product = self.validate_product_data_raw(product_data)
                    all_products.append(validated_product)
                    
                    # Adaugă o pauză mică pentru a fi respectuoși
                    time.sleep(0.5)
                
                # Log progresul la fiecare 10 produse
                if (i + 1) % 10 == 0:
                    logging.info(f"Procesat {i+1}/{len(product_urls)} URL-uri")
            
            # Pas 3: Analizează categoriile
            if 'st' in globals():
                st.info("📊 Pas 3: Analizarea categoriilor...")
            logging.info("Analizez categoriile")
            
            analysis_result = self.analyze_darwin_categories(all_products)
            
            # Pas 4: Exportă în CSV și JSON
            if 'st' in globals():
                st.info("💾 Pas 4: Exportarea datelor...")
            logging.info("Exportez datele")
            
            csv_filename = self.export_to_csv(all_products)
            json_filename = self.export_to_json(all_products)
            
            self.scraping_stats["end_time"] = datetime.now()
            self.scraping_stats["categories_found"] = len(self.categories_found)
            self.scraping_stats["duration"] = (
                self.scraping_stats["end_time"] - self.scraping_stats["start_time"]
            ).total_seconds()
            
            logging.info(f"Extragerea completă finalizată în {self.scraping_stats['duration']:.2f} secunde")
            
            return {
                "success": True,
                "products": all_products,
                "analysis": analysis_result,
                "csv_file": csv_filename,
                "json_file": json_filename,
                "statistics": self.scraping_stats,
                "failed_urls": self.failed_urls
            }
            
        except Exception as e:
            error_msg = f"Eroare în procesul de extragere: {str(e)}"
            logging.error(error_msg)
            if 'st' in globals():
                st.error(f"❌ {error_msg}")
            
            return {
                "success": False,
                "error": str(e),
                "statistics": self.scraping_stats,
                "failed_urls": self.failed_urls
            }


# Aplicația Streamlit
def main():
    """Interfața principală Streamlit"""
    st.set_page_config(
        page_title="Darwin.md Product Scraper",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizat pentru o interfață mai frumoasă
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
        color: white;
    }
    .stats-container {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .category-box {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📱 Darwin.md Product Scraper</h1>
        <p>Agent AI inteligent pentru extragerea datelor de pe Darwin.md</p>
        <p><small>Construit pentru integrarea cu Telegram Bot + ChromaDB</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("🔧 Configurare")
        
        # Configurare OpenAI
        st.subheader("🤖 Setări OpenAI")
        openai_api_key = st.text_input("Cheia API:", type="password", help="Cheia ta OpenAI API")
        openai_model = st.selectbox("Model:", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])
        
        if not openai_api_key:
            st.error("❌ Este necesară cheia OpenAI API")
            st.stop()
        
        # Opțiuni de scraping
        st.subheader("⚙️ Opțiuni de Scraping")
        max_products = st.number_input("Produse Maximum:", min_value=1, max_value=5000, value=100)
        
        # Status biblioteci
        st.subheader("📚 Status Biblioteci")
        col1, col2 = st.columns(2)
        with col1:
            st.write("✅ SeleniumBase" if SELENIUMBASE_AVAILABLE else "❌ SeleniumBase")
            st.write("✅ BeautifulSoup" if BEAUTIFULSOUP_AVAILABLE else "❌ BeautifulSoup")
        with col2:
            st.write("✅ DrissionPage" if DRISSIONPAGE_AVAILABLE else "❌ DrissionPage")
            st.write("✅ OpenAI Ready" if openai_api_key else "❌ Fără Cheie API")
        
        # Informații despre Darwin.md
        st.subheader("🏪 Despre Darwin.md")
        st.info("""
        **Site Țintă:** https://darwin.md
        
        **Categorii Suportate:**
        - Telefoane & Smartphone-uri
        - Laptopuri & Tablete
        - Audio & Gaming
        - Smart Home & Accesorii
        - Electronice Bucătărie
        - Componente PC
        """)
    
    # Interfața principală
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Scraper", "📊 Analiză", "📁 Export", "ℹ️ Informații"])
    
    with tab1:
        st.header("🛒 Darwin.md Product Scraper")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("**Țintă:** https://darwin.md/sitemap.xml")
            st.info("**Ieșire:** Fișiere CSV și JSON gata pentru Telegram Bot + ChromaDB")
        
        with col2:
            if st.button("🚀 Începe Extragerea", type="primary", use_container_width=True):
                try:
                    # Inițializează scraper-ul
                    with st.spinner("🔄 Inițializez scraper-ul..."):
                        scraper = DarwinProductScraper(openai_api_key, openai_model)
                    
                    # Rulează extragerea
                    with st.spinner("🔄 Rulează extragerea completă..."):
                        results = scraper.run_complete_extraction(max_products)
                    
                    if results.get("success"):
                        st.success("✅ Extragerea s-a completat cu succes!")
                        
                        # Stochează rezultatele în session state
                        st.session_state["extraction_results"] = results
                        st.session_state["scraper"] = scraper
                        
                        # Statistici rapide
                        stats = results["statistics"]
                        analysis = results["analysis"]
                        
                        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("URL-uri Găsite", stats["urls_discovered"])
                        col2.metric("Produse Extrase", stats["products_extracted"])
                        col3.metric("Rata de Succes", f"{analysis['quality_score']:.1f}%")
                        col4.metric("Categorii", analysis["category_count"])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Durata procesului
                        duration_minutes = stats.get("duration", 0) / 60
                        st.info(f"⏱️ Procesul a durat: {duration_minutes:.1f} minute")
                        
                    else:
                        st.error(f"❌ Extragerea a eșuat: {results.get('error')}")
                        
                except Exception as e:
                    st.error(f"❌ Eroare: {str(e)}")
    
    with tab2:
        st.header("📊 Rezultatele Analizei")
        
        if "extraction_results" in st.session_state:
            results = st.session_state["extraction_results"]
            analysis = results["analysis"]
            
            # Statistici generale
            st.subheader("📈 Statistici Generale")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Produse", analysis["total_products"])
            col2.metric("Produse Valide", analysis["valid_products"])
            col3.metric("Scorul Calității", f"{analysis['quality_score']:.1f}%")
            
            # Defalcare categorii
            st.subheader("🏷️ Defalcare Categorii")
            categories = analysis["categories"]
            
            if categories:
                # Creează DataFrame pentru afișare
                category_data = []
                for cat_name, cat_data in categories.items():
                    category_data.append({
                        "Categoria": cat_name,
                        "Produse": cat_data["count"],
                        "Preț Mediu (MDL)": f"{cat_data['avg_price']:.2f}",
                        "Preț Min (MDL)": f"{cat_data['min_price']:.2f}",
                        "Preț Max (MDL)": f"{cat_data['max_price']:.2f}"
                    })
                
                df = pd.DataFrame(category_data)
                st.dataframe(df, use_container_width=True)
                
                # Grafic categorii
                st.subheader("📊 Distribuția Categoriilor")
                fig_data = df.set_index("Categoria")["Produse"]
                st.bar_chart(fig_data)
                
                # Categoria cea mai populară
                st.success(f"🏆 Categoria cea mai populară: **{analysis['most_popular_category']}**")
            else:
                st.info("Nu există categorii de afișat")
        else:
            st.info("👆 Rulează mai întâi extragerea pentru a vedea rezultatele analizei")
    
    with tab3:
        st.header("📁 Export și Descărcare")
        
        if "extraction_results" in st.session_state:
            results = st.session_state["extraction_results"]
            
            col1, col2 = st.columns(2)
            
            # Export CSV
            with col1:
                st.subheader("📄 Fișier CSV")
                st.success(f"✅ CSV gata: {results['csv_file']}")
                
                try:
                    with open(results['csv_file'], 'r', encoding='utf-8') as f:
                        csv_content = f.read()
                    
                    st.download_button(
                        label="⬇️ Descarcă CSV",
                        data=csv_content,
                        file_name=results['csv_file'],
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Preview CSV
                    df = pd.read_csv(results['csv_file'])
                    st.write(f"**Preview ({len(df)} produse):**")
                    st.dataframe(df.head(5), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Eroare la citirea fișierului CSV: {str(e)}")
            
            # Export JSON
            with col2:
                st.subheader("📋 Fișier JSON")
                st.success(f"✅ JSON gata: {results['json_file']}")
                
                try:
                    with open(results['json_file'], 'r', encoding='utf-8') as f:
                        json_content = f.read()
                    
                    st.download_button(
                        label="⬇️ Descarcă JSON",
                        data=json_content,
                        file_name=results['json_file'],
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    # Info despre JSON
                    st.info("**Format:** JSON cu metadate\n**Folosire:** Procesare automată, API-uri")
                    
                except Exception as e:
                    st.error(f"Eroare la citirea fișierului JSON: {str(e)}")
            
            # Statistici export
            st.subheader("📊 Informații Export")
            stats = results["statistics"]
            analysis = results["analysis"]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Produse Exportate", analysis["valid_products"])
            col2.metric("URL-uri Eșuate", len(results["failed_urls"]))
            col3.metric("Rata de Succes", f"{analysis['quality_score']:.1f}%")
            
            # URL-uri eșuate
            if results["failed_urls"]:
                st.subheader("⚠️ URL-uri Eșuate")
                with st.expander(f"Vezi {len(results['failed_urls'])} URL-uri eșuate"):
                    for url in results["failed_urls"]:
                        st.write(f"• {url}")
        else:
            st.info("👆 Rulează mai întâi extragerea pentru a genera fișierele de export")
    
    with tab4:
        st.header("ℹ️ Informații despre Scraper")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Caracteristici")
            st.markdown("""
            **Agent AI Inteligent:**
            - Folosește OpenAI GPT pentru procesare avansată
            - Metode multiple de extragere (DrissionPage, SeleniumBase, BeautifulSoup)
            - Validare automată a datelor
            - Analiză categorii dinamică
            
            **Capabilități de Scraping:**
            - Analiză sitemap XML completă
            - Detectare automată URL-uri produse
            - Extragere robustă de date
            - Gestionare erori avansată
            
            **Export Multiple:**
            - CSV pentru ChromaDB
            - JSON cu metadate
            - Compatibil cu Telegram Bot
            """)
        
        with col2:
            st.subheader("🛠️ Tehnologii")
            st.markdown("""
            **Framework AI:**
            - Agno Agent Framework
            - OpenAI GPT Models
            - Tool-based Architecture
            
            **Web Scraping:**
            - DrissionPage (rapid)
            - SeleniumBase (JavaScript)
            - BeautifulSoup (fallback)
            - Requests HTTP
            
            **Interfață:**
            - Streamlit
            - Pandas pentru analiză
            - Progress tracking
            """)
        
        st.subheader("🔍 Despre Darwin.md")
        st.markdown("""
        **Darwin.md** este unul dintre cei mai mari retaileri de electronice din Moldova, oferind:
        
        - **Smartphone-uri și Telefoane** - iPhone, Samsung, Xiaomi, etc.
        - **Laptopuri și PC-uri** - Dell, HP, Lenovo, sisteme gaming
        - **Audio și Gaming** - Căști, boxe, console, accesorii
        - **Smart Home** - Dispozitive inteligente, senzori, automatizare
        - **Electronice Bucătărie** - Aparate de bucătărie moderne
        
        **Avantajele scraping-ului Darwin.md:**
        - Catalog vast de produse
        - Prețuri competitive în MDL
        - Descrieri detaliate în română
        - Imagini de înaltă calitate
        - Categorii bine organizate
        """)
        
        st.subheader("⚙️ Configurare Recomandată")
        st.markdown("""
        **Pentru rezultate optime:**
        
        1. **Model OpenAI:** GPT-4o pentru cea mai bună acuratețe
        2. **Produse Maximum:** 100-500 pentru testare, 1000+ pentru producție
        3. **Biblioteci:** Instalează toate bibliotecile pentru redundanță
        4. **Rate Limiting:** Pauze de 0.5s între cereri pentru respectul site-ului
        
        **Cerințe sistem:**
        - Python 3.8+
        - 4GB RAM minimum
        - Conexiune internet stabilă
        - Chei API valide
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <p>🤖 <strong>AI Web Scraping Agent pentru Darwin.md</strong></p>
        <p>Construit cu Agno Framework + Streamlit | Optimizat pentru Telegram Bot + ChromaDB</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Darwin.md scraper utilities')
    parser.add_argument('--sitemap-summary', action='store_true', help='Fetch sitemap index and write a JSON summary')
    parser.add_argument('--sitemap-url', type=str, default='https://darwin.md/sitemap.xml', help='Sitemap index URL')
    parser.add_argument('--output', type=str, default=None, help='Output JSON file')
    args = parser.parse_args()

    if args.sitemap_summary:
        # instantiate scraper with minimal requirement - try to get API key helper
        api_key = None
        try:
            from openai_config import get_openai_api_key as _gk
            api_key = _gk()
        except Exception:
            api_key = None

        fake_key = api_key or 'DUMMY_KEY'
        try:
            scraper = DarwinProductScraper(fake_key)
        except Exception:
            # create minimal stub and bind method
            class _Tmp: pass
            scraper = _Tmp()
            import types
            scraper.sitemap_index_summary = types.MethodType(DarwinProductScraper.sitemap_index_summary, scraper)

        summary = scraper.sitemap_index_summary(args.sitemap_url, output_file=args.output)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        main()