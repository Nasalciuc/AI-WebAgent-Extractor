#!/usr/bin/env python3
"""
Darwin.md Traffic Analysis Module
Modul pentru analizarea surselor de trafic pentru site-ul Darwin.md
"""

import requests
import json
import re
import time
import logging
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs
from collections import Counter
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add config directory to path for centralized environment management
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
try:
    from env_config import get_environment_config
    ENV_CONFIG_AVAILABLE = True
except ImportError:
    ENV_CONFIG_AVAILABLE = False

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_analyzer.log'),
        logging.StreamHandler()
    ]
)

# Încărcăm variabilele de mediu
load_dotenv()

class TrafficAnalyzer:
    """
    Analizor de trafic pentru Darwin.md și alte site-uri de e-commerce.
    Oferă funcționalități pentru analiza surselor de trafic, referrerilor
    și potențial integrare cu API-uri externe pentru date de trafic.
    """
    
    def __init__(self, target_domain: str = "darwin.md"):
        """Inițializează analizorul de trafic pentru domeniul specificat"""
        self.target_domain = target_domain
        
        # Folosește noul sistem centralizat de configurare dacă este disponibil
        if ENV_CONFIG_AVAILABLE:
            config = get_environment_config()
            self.semrush_api_key = config.get_semrush_api_key() or ""
            self.similarweb_api_key = config.get_similarweb_api_key() or ""
        else:
            # Fallback la metoda veche
            self.semrush_api_key = os.getenv("SEMRUSH_API_KEY")
            self.similarweb_api_key = os.getenv("SIMILARWEB_API_KEY")
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0'
        ]
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agents[0]
        }
        self.referer_patterns = {
            'google': [r'google\.', r'\.google\.'],
            'facebook': [r'facebook\.com', r'fb\.com', r'fb\.me'],
            'instagram': [r'instagram\.com', r'instagr\.am'],
            'youtube': [r'youtube\.com', r'youtu\.be'],
            'direct': [],
            'tiktok': [r'tiktok\.com', r't\.co'],
            'mail': [r'mail\.', r'gmail\.com', r'yahoo\.', r'outlook\.com'],
            'yandex': [r'yandex\.'],
            'telegram': [r't\.me', r'telegram\.']
        }
        
        # Inițializăm stocarea de date
        self.data = {
            "referrers": [],
            "traffic_sources": {},
            "search_keywords": [],
            "utm_campaigns": [],
            "popular_pages": [],
            "external_analysis": {}
        }
    
    def analyze_url_referrers(self, urls: List[str], max_workers: int = 10) -> Dict[str, Any]:
        """
        Analizează referrer-ii pentru o listă de URL-uri trimițând cereri cu diferite referreri
        și verifică care sunt acceptate/respinse
        
        Args:
            urls: O listă de URL-uri de analizat
            max_workers: Numărul maxim de workeri concurenți
            
        Returns:
            Dict cu statistici despre referreri și acceptare
        """
        results = {
            "total_urls": len(urls),
            "successful_requests": 0,
            "referrer_stats": {},
            "top_referrers": [],
            "blocked_referrers": []
        }
        
        # Listă de referreri de testat
        test_referrers = [
            "https://www.google.com/search?q=darwin+moldova+telefoane",
            "https://www.facebook.com/",
            "https://www.instagram.com/",
            "https://yandex.ru/search/?text=darwin+moldova",
            "https://ro.pinterest.com/",
            "https://www.tiktok.com/",
            "https://t.me/share",
            None  # Direct traffic
        ]
        
        # Funcție pentru worker
        def check_referrer(url, referrer):
            headers = self.headers.copy()
            if referrer:
                headers['Referer'] = referrer
                referrer_name = urlparse(referrer).netloc
            else:
                referrer_name = "direct"
            
            try:
                resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                success = resp.status_code == 200
                content_length = len(resp.content)
                return {
                    "url": url,
                    "referrer": referrer,
                    "referrer_name": referrer_name,
                    "status_code": resp.status_code,
                    "success": success,
                    "content_length": content_length
                }
            except Exception as e:
                return {
                    "url": url,
                    "referrer": referrer,
                    "referrer_name": referrer_name,
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # Execută verificările
        all_results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_data = {}
            for url in urls[:5]:  # Limităm la primele 5 URL-uri pentru a nu supraîncărca
                for referrer in test_referrers:
                    future = executor.submit(check_referrer, url, referrer)
                    future_to_data[future] = (url, referrer)
            
            for future in as_completed(future_to_data):
                url, referrer = future_to_data[future]
                try:
                    data = future.result()
                    all_results.append(data)
                    if data["success"]:
                        results["successful_requests"] += 1
                except Exception as e:
                    logging.error(f"Error processing {url} with referrer {referrer}: {e}")
        
        # Analizează rezultatele
        referrer_stats = {}
        for res in all_results:
            ref_name = res["referrer_name"]
            if ref_name not in referrer_stats:
                referrer_stats[ref_name] = {"total": 0, "success": 0, "failure": 0, "avg_content_length": 0}
            
            referrer_stats[ref_name]["total"] += 1
            if res["success"]:
                referrer_stats[ref_name]["success"] += 1
                referrer_stats[ref_name]["avg_content_length"] += res["content_length"]
            else:
                referrer_stats[ref_name]["failure"] += 1
        
        # Calculează medii și rate
        for ref, stats in referrer_stats.items():
            if stats["success"] > 0:
                stats["avg_content_length"] = stats["avg_content_length"] / stats["success"]
            stats["success_rate"] = (stats["success"] / stats["total"]) * 100
        
        # Sortează pentru top referreri
        top_referrers = sorted(
            referrer_stats.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )
        
        # Găsește referreri blocați
        blocked_referrers = [
            ref for ref, stats in referrer_stats.items()
            if stats["success_rate"] < 50 and stats["total"] >= 2
        ]
        
        results["referrer_stats"] = referrer_stats
        results["top_referrers"] = top_referrers[:5]
        results["blocked_referrers"] = blocked_referrers
        results["raw_results"] = all_results
        
        # Stochează datele pentru analize ulterioare
        self.data["referrers"] = all_results
        
        return results
    
    def extract_utm_parameters(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extrage și analizează parametri UTM din URL-uri pentru a identifica
        campanii de marketing și surse de trafic.
        
        Args:
            urls: O listă de URL-uri de analizat
            
        Returns:
            Dict cu statistici despre parametrii UTM găsiți
        """
        results = {
            "total_urls": len(urls),
            "urls_with_utm": 0,
            "utm_sources": Counter(),
            "utm_mediums": Counter(),
            "utm_campaigns": Counter(),
            "utm_terms": Counter(),
            "utm_contents": Counter(),
            "complete_utm_data": []
        }
        
        for url in urls:
            try:
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                
                utm_data = {
                    "url": url,
                    "utm_source": query_params.get("utm_source", [None])[0],
                    "utm_medium": query_params.get("utm_medium", [None])[0],
                    "utm_campaign": query_params.get("utm_campaign", [None])[0],
                    "utm_term": query_params.get("utm_term", [None])[0],
                    "utm_content": query_params.get("utm_content", [None])[0]
                }
                
                has_utm = any([v for k, v in utm_data.items() if k != "url" and v is not None])
                
                if has_utm:
                    results["urls_with_utm"] += 1
                    results["complete_utm_data"].append(utm_data)
                    
                    # Actualizăm statisticile
                    if utm_data["utm_source"]:
                        results["utm_sources"][utm_data["utm_source"]] += 1
                    if utm_data["utm_medium"]:
                        results["utm_mediums"][utm_data["utm_medium"]] += 1
                    if utm_data["utm_campaign"]:
                        results["utm_campaigns"][utm_data["utm_campaign"]] += 1
                    if utm_data["utm_term"]:
                        results["utm_terms"][utm_data["utm_term"]] += 1
                    if utm_data["utm_content"]:
                        results["utm_contents"][utm_data["utm_content"]] += 1
            
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
        
        # Convertim Counter în liste pentru JSON
        results["utm_sources"] = dict(results["utm_sources"].most_common())
        results["utm_mediums"] = dict(results["utm_mediums"].most_common())
        results["utm_campaigns"] = dict(results["utm_campaigns"].most_common())
        results["utm_terms"] = dict(results["utm_terms"].most_common())
        results["utm_contents"] = dict(results["utm_contents"].most_common())
        
        # Adăugăm în datele globale
        self.data["utm_campaigns"] = results["complete_utm_data"]
        
        return results
    
    def analyze_search_keywords(self, urls: List[str]) -> Dict[str, Any]:
        """
        Analizează URL-urile pentru a extrage cuvintele cheie de căutare
        din parametrii q, query, search, etc.
        
        Args:
            urls: O listă de URL-uri de analizat
            
        Returns:
            Dict cu statistici despre cuvintele cheie găsite
        """
        results = {
            "total_urls": len(urls),
            "urls_with_keywords": 0,
            "top_keywords": Counter(),
            "search_engines": Counter(),
            "keyword_details": []
        }
        
        search_param_keys = ["q", "query", "search", "text", "p", "searchfor"]
        search_engine_patterns = {
            "google": r"google\.",
            "yandex": r"yandex\.",
            "bing": r"bing\.",
            "yahoo": r"yahoo\.",
            "duckduckgo": r"duckduckgo\.",
        }
        
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc
                query_params = parse_qs(parsed.query)
                
                # Identifică search engine
                search_engine = "unknown"
                for engine, pattern in search_engine_patterns.items():
                    if re.search(pattern, domain):
                        search_engine = engine
                        break
                
                # Extrage cuvintele cheie de căutare
                keyword = None
                for param in search_param_keys:
                    if param in query_params:
                        keyword = query_params[param][0]
                        break
                
                if keyword:
                    results["urls_with_keywords"] += 1
                    results["top_keywords"][keyword.lower()] += 1
                    results["search_engines"][search_engine] += 1
                    
                    results["keyword_details"].append({
                        "url": url,
                        "search_engine": search_engine,
                        "keyword": keyword,
                        "date_found": datetime.now().isoformat()
                    })
            
            except Exception as e:
                logging.error(f"Error processing URL {url} for keywords: {e}")
        
        # Convertim Counter în liste pentru JSON
        results["top_keywords"] = dict(results["top_keywords"].most_common(20))
        results["search_engines"] = dict(results["search_engines"].most_common())
        
        # Stochează datele pentru analize ulterioare
        self.data["search_keywords"] = results["keyword_details"]
        
        return results
    
    def get_traffic_data_from_semrush(self) -> Dict[str, Any]:
        """
        Obține date despre trafic folosind API-ul SEMrush
        
        Returns:
            Dict cu date despre trafic de la SEMrush
        """
        if not self.semrush_api_key:
            return {"error": "SEMrush API key not configured", "success": False}
        
        try:
            # Endpoint-ul și parametrii
            url = "https://api.semrush.com"
            params = {
                "type": "domain_ranks",
                "key": self.semrush_api_key,
                "export_columns": "Dn,Rk,Or,Ot,Oc,Ad,At,Ac",
                "domain": self.target_domain,
                "database": "ro"  # Database pentru România
            }
            
            # Face cererea
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return {
                    "success": False, 
                    "error": f"API error: {response.status_code}", 
                    "response": response.text
                }
            
            # Parsează răspunsul (CSV)
            lines = response.text.strip().split("\n")
            if len(lines) < 2:
                return {"success": False, "error": "No data returned"}
            
            headers = lines[0].split(";")
            data = lines[1].split(";")
            
            result = dict(zip(headers, data))
            result["success"] = True
            
            # Adăugăm la datele globale
            self.data["external_analysis"]["semrush"] = result
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting SEMrush data: {e}")
            return {"success": False, "error": str(e)}
    
    def get_traffic_data_from_similarweb(self) -> Dict[str, Any]:
        """
        Obține date despre trafic folosind API-ul SimilarWeb
        
        Returns:
            Dict cu date despre trafic de la SimilarWeb
        """
        if not self.similarweb_api_key:
            return {"error": "SimilarWeb API key not configured", "success": False}
        
        try:
            # Endpoint-ul
            url = f"https://api.similarweb.com/v1/website/{self.target_domain}/traffic-sources/overview"
            
            headers = {
                "accept": "application/json",
                "api-key": self.similarweb_api_key
            }
            
            # Face cererea
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return {
                    "success": False, 
                    "error": f"API error: {response.status_code}", 
                    "response": response.text
                }
            
            # Parsează răspunsul JSON
            data = response.json()
            result = {
                "success": True,
                "domain": self.target_domain,
                "traffic_sources": data.get("overview", {}),
                "date": datetime.now().isoformat()
            }
            
            # Adăugăm la datele globale
            self.data["external_analysis"]["similarweb"] = data
            self.data["traffic_sources"] = data.get("overview", {})
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting SimilarWeb data: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_site_popularity(self) -> Dict[str, Any]:
        """
        Analizează popularitatea site-ului folosind datele disponibile
        
        Returns:
            Dict cu statistici de popularitate
        """
        results = {
            "domain": self.target_domain,
            "date": datetime.now().isoformat(),
            "metrics": {},
            "traffic_sources": {},
            "top_referrers": [],
            "popular_pages": [],
            "search_engines": {},
            "social_media": {}
        }
        
        # Combină datele din surse externe și analizele proprii
        if "semrush" in self.data["external_analysis"]:
            semrush_data = self.data["external_analysis"]["semrush"]
            results["metrics"]["organic_traffic"] = semrush_data.get("Ot", "N/A")
            results["metrics"]["organic_keywords"] = semrush_data.get("Or", "N/A")
            results["metrics"]["organic_cost"] = semrush_data.get("Oc", "N/A")
        
        if "similarweb" in self.data["external_analysis"]:
            similarweb_data = self.data["external_analysis"]["similarweb"]
            if "traffic_sources" in similarweb_data:
                results["traffic_sources"] = similarweb_data["traffic_sources"]
        
        if self.data["traffic_sources"]:
            results["traffic_sources"] = self.data["traffic_sources"]
        
        # Adaugă top referreri din analizele proprii
        if self.data["referrers"]:
            referrer_counts = Counter()
            for ref in self.data["referrers"]:
                if ref.get("success") and ref.get("referrer_name"):
                    referrer_counts[ref["referrer_name"]] += 1
            
            results["top_referrers"] = [
                {"domain": domain, "count": count} 
                for domain, count in referrer_counts.most_common(10)
            ]
        
        return results
    
    def generate_traffic_report(self, output_dir: str = "reports") -> Dict[str, Any]:
        """
        Generează un raport complet de trafic combinând toate datele disponibile
        
        Args:
            output_dir: Directorul în care să salveze raportul
            
        Returns:
            Dict cu calea către raport și sumarul
        """
        # Creează directorul dacă nu există
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"traffic_report_{self.target_domain}_{timestamp}.json")
        csv_file = os.path.join(output_dir, f"traffic_sources_{self.target_domain}_{timestamp}.csv")
        chart_file = os.path.join(output_dir, f"traffic_chart_{self.target_domain}_{timestamp}.png")
        
        # Obține date de la API-uri externe dacă nu sunt deja disponibile
        if not self.data["external_analysis"].get("semrush"):
            self.get_traffic_data_from_semrush()
        
        if not self.data["external_analysis"].get("similarweb"):
            self.get_traffic_data_from_similarweb()
        
        # Generează raportul final
        report = {
            "domain": self.target_domain,
            "report_date": datetime.now().isoformat(),
            "traffic_summary": self.analyze_site_popularity(),
            "external_data": {
                "semrush": self.data["external_analysis"].get("semrush", {}),
                "similarweb": self.data["external_analysis"].get("similarweb", {})
            },
            "referrers_analysis": {
                "top_referrers": [r for r in self.data["referrers"] if r.get("success")][:10],
                "blocked_referrers": [r for r in self.data["referrers"] if not r.get("success")][:10]
            },
            "marketing_campaigns": {
                "utm_sources": Counter([u.get("utm_source") for u in self.data["utm_campaigns"] if u.get("utm_source")]).most_common(10),
                "utm_mediums": Counter([u.get("utm_medium") for u in self.data["utm_campaigns"] if u.get("utm_medium")]).most_common(10),
                "utm_campaigns": Counter([u.get("utm_campaign") for u in self.data["utm_campaigns"] if u.get("utm_campaign")]).most_common(10)
            },
            "search_analysis": {
                "top_keywords": Counter([k.get("keyword") for k in self.data["search_keywords"] if k.get("keyword")]).most_common(20),
                "search_engines": Counter([k.get("search_engine") for k in self.data["search_keywords"] if k.get("search_engine")]).most_common()
            }
        }
        
        # Salvează raportul în JSON
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Creează CSV pentru sursele de trafic
        traffic_sources = []
        if self.data["traffic_sources"]:
            for source, value in self.data["traffic_sources"].items():
                traffic_sources.append({"source": source, "percentage": value})
        
        if traffic_sources:
            df = pd.DataFrame(traffic_sources)
            df.to_csv(csv_file, index=False)
            
            # Generează grafic pentru vizualizare
            try:
                plt.figure(figsize=(10, 6))
                plt.bar(df['source'], df['percentage'])
                plt.title(f'Traffic Sources for {self.target_domain}')
                plt.xlabel('Source')
                plt.ylabel('Percentage %')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(chart_file)
            except Exception as e:
                logging.error(f"Error generating chart: {e}")
        
        return {
            "success": True,
            "report_file": report_file,
            "csv_file": csv_file if traffic_sources else None,
            "chart_file": chart_file if traffic_sources else None,
            "summary": report["traffic_summary"]
        }
    
    def analyze_traffic_from_sitemap(self, sitemap_url: str) -> Dict[str, Any]:
        """
        Analizează traficul potențial în baza sitemap-ului site-ului
        
        Args:
            sitemap_url: URL-ul către sitemap-ul site-ului
            
        Returns:
            Dict cu analiză de trafic bazată pe structura sitemap-ului
        """
        from xml.etree import ElementTree as ET
        
        try:
            # Descarcă sitemap-ul
            headers = self.headers.copy()
            response = requests.get(sitemap_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Extrage URL-urile
            urls = []
            
            # Check if it's a sitemap index
            sitemaps = root.findall('.//ns:sitemap', namespace)
            if sitemaps:
                for sitemap in sitemaps:
                    loc = sitemap.find('ns:loc', namespace)
                    if loc is not None and loc.text:
                        # Descarcă sub-sitemap-ul
                        sub_url = loc.text.strip()
                        try:
                            sub_response = requests.get(sub_url, headers=headers, timeout=15)
                            sub_response.raise_for_status()
                            sub_root = ET.fromstring(sub_response.content)
                            for url in sub_root.findall('.//ns:url', namespace):
                                loc = url.find('ns:loc', namespace)
                                if loc is not None and loc.text:
                                    urls.append(loc.text.strip())
                        except Exception as e:
                            logging.error(f"Error processing sub-sitemap {sub_url}: {e}")
            else:
                # Direct urlset
                for url in root.findall('.//ns:url', namespace):
                    loc = url.find('ns:loc', namespace)
                    if loc is not None and loc.text:
                        urls.append(loc.text.strip())
            
            # Limitează numărul de URL-uri pentru analiză
            sample_urls = urls[:100]  # Analizăm doar primele 100 pentru performanță
            
            # Analizează referreri
            referrer_analysis = self.analyze_url_referrers(sample_urls[:10])
            
            # Analizează UTM parametri
            utm_analysis = self.extract_utm_parameters(sample_urls)
            
            # Analizează cuvinte cheie de căutare
            keyword_analysis = self.analyze_search_keywords(sample_urls)
            
            # Clasifică URL-urile
            url_categories = self.classify_urls(sample_urls)
            
            return {
                "success": True,
                "sitemap_url": sitemap_url,
                "total_urls": len(urls),
                "analyzed_urls": len(sample_urls),
                "referrer_analysis": referrer_analysis,
                "utm_analysis": utm_analysis,
                "keyword_analysis": keyword_analysis,
                "url_categories": url_categories
            }
            
        except Exception as e:
            logging.error(f"Error analyzing traffic from sitemap: {e}")
            return {"success": False, "error": str(e), "sitemap_url": sitemap_url}
    
    def classify_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Clasifică URL-urile în categorii (produse, categorii, blog, etc.)
        
        Args:
            urls: O listă de URL-uri pentru clasificare
            
        Returns:
            Dict cu URL-uri clasificate
        """
        categories = {
            "products": [],
            "categories": [],
            "blog": [],
            "static": [],
            "user": [],
            "other": []
        }
        
        for url in urls:
            path = urlparse(url).path.lower()
            
            # Clasificare bazată pe modele de URL-uri comune pentru e-commerce
            if re.search(r'/(product|produs|p)/|/[a-z0-9-]+/[a-z0-9-]+-p\d+|/[a-z0-9-]+-\d+$', path):
                categories["products"].append(url)
            elif re.search(r'/(categor|department|section)/', path) or re.search(r'/(telefoane|laptopuri|tablete|accesorii)/$', path):
                categories["categories"].append(url)
            elif re.search(r'/(blog|news|article|post)/', path):
                categories["blog"].append(url)
            elif re.search(r'/(about|contact|faq|help|terms|privacy|shipping|return|info)$', path):
                categories["static"].append(url)
            elif re.search(r'/(user|account|profile|wishlist|cart|checkout|order)/', path):
                categories["user"].append(url)
            else:
                categories["other"].append(url)
        
        # Calculează statistici
        stats = {category: len(urls) for category, urls in categories.items()}
        
        return {
            "categories": categories,
            "stats": stats,
            "total": len(urls)
        }

    def identify_social_traffic_sources(self, sample_pages: int = 10) -> Dict[str, Any]:
        """
        Identifică și analizează sursele de trafic social prin scanarea pentru 
        butoane de share și integrări social media
        
        Args:
            sample_pages: Numărul de pagini de analizat
            
        Returns:
            Dict cu sursele de trafic social identificate
        """
        social_platforms = {
            "facebook": [r'facebook\.com', r'fb-root', r'fb_iframe', r'Facebook\.init'],
            "instagram": [r'instagram\.com', r'insta-gallery', r'instagram-feed'],
            "twitter": [r'twitter\.com', r'twitter-share', r'twitter-follow'],
            "pinterest": [r'pinterest\.com', r'pin-it-button', r'pinit\.js'],
            "youtube": [r'youtube\.com', r'youtube-player', r'youtube-embed'],
            "tiktok": [r'tiktok\.com', r'tiktok-embed'],
            "linkedin": [r'linkedin\.com', r'linkedin-share'],
            "telegram": [r't\.me', r'telegram-share'],
            "whatsapp": [r'whatsapp:\/\/send', r'wa\.me']
        }
        
        # Obținem URL-urile pentru homepage + câteva produse/categorii
        urls = [f"https://{self.target_domain}/"]
        
        try:
            # Obținem câteva URL-uri din sitemap
            sitemap_url = f"https://{self.target_domain}/sitemap.xml"
            headers = self.headers.copy()
            response = requests.get(sitemap_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                url_elems = root.findall('.//ns:url/ns:loc', namespace)
                if url_elems:
                    for i, elem in enumerate(url_elems):
                        if i >= sample_pages:
                            break
                        if elem.text:
                            urls.append(elem.text.strip())
        except Exception as e:
            logging.warning(f"Could not get URLs from sitemap: {e}")
            # Fallback: generează câteva URL-uri tipice
            urls.extend([
                f"https://{self.target_domain}/telefoane",
                f"https://{self.target_domain}/laptopuri",
                f"https://{self.target_domain}/about",
                f"https://{self.target_domain}/contact"
            ])
        
        social_data = {
            "found_platforms": set(),
            "integration_count": {platform: 0 for platform in social_platforms},
            "share_buttons": {platform: 0 for platform in social_platforms},
            "urls_analyzed": len(urls)
        }
        
        # Analizează fiecare URL
        for url in urls:
            try:
                headers = self.headers.copy()
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    continue
                
                html_content = response.text.lower()
                
                # Verifică prezența fiecărei platforme
                for platform, patterns in social_platforms.items():
                    for pattern in patterns:
                        if re.search(pattern.lower(), html_content):
                            social_data["found_platforms"].add(platform)
                            social_data["integration_count"][platform] += 1
                            break
                
                # Verifică butoanele de share
                share_patterns = [
                    r'share-button', r'social-share', r'share-icon', 
                    r'social-media', r'social-links', r'social-icons',
                    r'share on', r'share this'
                ]
                
                for pattern in share_patterns:
                    if re.search(pattern, html_content):
                        for platform in social_platforms:
                            if platform in html_content[html_content.find(pattern)-50:html_content.find(pattern)+50]:
                                social_data["share_buttons"][platform] += 1
            
            except Exception as e:
                logging.error(f"Error analyzing social media on {url}: {e}")
        
        # Convertește set în listă pentru JSON
        social_data["found_platforms"] = list(social_data["found_platforms"])
        
        # Sortează platformele după frecvență
        social_data["top_platforms"] = sorted(
            social_data["integration_count"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return social_data

# Exemplu de utilizare
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Darwin.md Traffic Analyzer")
    parser.add_argument("--domain", type=str, default="darwin.md", help="Domain to analyze")
    parser.add_argument("--sitemap", type=str, help="Sitemap URL to analyze")
    parser.add_argument("--report", action="store_true", help="Generate full traffic report")
    parser.add_argument("--social", action="store_true", help="Analyze social traffic sources")
    
    args = parser.parse_args()
    
    analyzer = TrafficAnalyzer(args.domain)
    
    if args.sitemap:
        print(f"Analyzing traffic from sitemap: {args.sitemap}")
        result = analyzer.analyze_traffic_from_sitemap(args.sitemap)
        print(json.dumps(result, indent=2))
    
    if args.social:
        print(f"Analyzing social traffic sources for {args.domain}")
        result = analyzer.identify_social_traffic_sources()
        print(json.dumps(result, indent=2))
    
    if args.report:
        print(f"Generating traffic report for {args.domain}")
        result = analyzer.generate_traffic_report()
        print(f"Report saved to: {result.get('report_file')}")
        if result.get('csv_file'):
            print(f"CSV saved to: {result.get('csv_file')}")
        if result.get('chart_file'):
            print(f"Chart saved to: {result.get('chart_file')}")