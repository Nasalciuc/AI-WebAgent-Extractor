"""
Analizor avansat pentru produsele Darwin.md
Oferă funcționalități de categorizare și extragere de atribute
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from urllib.parse import urlparse, unquote
import logging
from collections import defaultdict

@dataclass
class ProductAttributes:
    """Atributele extrase ale unui produs"""
    brand: Optional[str] = None
    model: Optional[str] = None
    series: Optional[str] = None
    capacity: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    currency: str = "MDL"
    category: Optional[str] = None
    subcategory: Optional[str] = None
    specs: Dict[str, str] = None
    
    def __post_init__(self):
        if self.specs is None:
            self.specs = {}

class DarwinProductAnalyzer:
    """
    Analizor specializat pentru produsele Darwin.md
    - Extrage atribute din URL și titlu
    - Categorizează produsele
    - Detectează specificații tehnice
    """
    
    def __init__(self):
        # Configurare reguli de categorizare
        self._init_category_rules()
        self._init_brand_patterns()
        self._init_spec_patterns()
        
    def _init_category_rules(self):
        """Inițializează regulile de categorizare"""
        self.category_rules = {
            # Telefoane și Accesorii
            "smartphones": {
                "patterns": [r"telefon", r"smartphone", r"iphone", r"samsung", r"huawei", r"xiaomi"],
                "subcategories": {
                    "flagship": [r"pro\s*max", r"ultra", r"premium"],
                    "midrange": [r"lite", r"se", r"regular"],
                    "budget": [r"redmi", r"poco"]
                }
            },
            "phone_accessories": {
                "patterns": [r"husa", r"incarcator", r"cablu", r"folie", r"protectie"],
                "subcategories": {
                    "cases": [r"husa", r"carcasa"],
                    "chargers": [r"incarcator", r"alimentator"],
                    "cables": [r"cablu", r"adaptor"],
                    "protection": [r"folie", r"sticla", r"protectie"]
                }
            },
            
            # Laptopuri și Accesorii
            "laptops": {
                "patterns": [r"laptop", r"notebook", r"macbook"],
                "subcategories": {
                    "gaming": [r"gaming", r"rtx", r"gtx"],
                    "business": [r"thinkpad", r"elitebook", r"probook"],
                    "ultrabook": [r"air", r"slim", r"ultra"],
                    "workstation": [r"workstation", r"studio", r"pro"]
                }
            },
            "laptop_accessories": {
                "patterns": [r"cooling", r"pad", r"geanta", r"rucsac"],
                "subcategories": {
                    "cooling": [r"cooling", r"racire", r"pad"],
                    "bags": [r"geanta", r"rucsac", r"husa laptop"],
                    "docking": [r"dock", r"docking", r"statie"]
                }
            },
            
            # Audio
            "audio": {
                "patterns": [r"casti", r"boxe", r"speaker", r"audio"],
                "subcategories": {
                    "headphones": [r"casti", r"headphones"],
                    "earbuds": [r"airpods", r"tws", r"buds"],
                    "speakers": [r"boxe", r"speaker", r"difuzor"],
                    "microphones": [r"microfon", r"lavaliera"]
                }
            }
        }
        
    def _init_brand_patterns(self):
        """Inițializează modelele pentru detectarea brandurilor"""
        self.brand_patterns = {
            # Telefoane
            "apple": [r"iphone", r"airpods"],
            "samsung": [r"samsung", r"galaxy"],
            "xiaomi": [r"xiaomi", r"redmi", r"poco"],
            "huawei": [r"huawei", r"honor"],
            
            # Laptopuri
            "lenovo": [r"lenovo", r"thinkpad", r"ideapad"],
            "hp": [r"hp", r"hewlett.?packard", r"elitebook", r"probook"],
            "dell": [r"dell", r"xps", r"latitude", r"precision"],
            "asus": [r"asus", r"zenbook", r"vivobook", r"rog"],
            
            # Audio
            "sony": [r"sony", r"wh-\d{4}", r"wf-\d{4}"],
            "bose": [r"bose"],
            "jbl": [r"jbl"],
            "airpods": [r"airpods"]
        }
        
    def _init_spec_patterns(self):
        """Inițializează modelele pentru extragerea specificațiilor"""
        self.spec_patterns = {
            # Specificații generale
            "storage": [
                (r"(\d+)\s*GB", "storage_gb"),
                (r"(\d+)\s*TB", "storage_tb"),
                (r"(\d+)\s*Go", "storage_gb")
            ],
            "memory": [
                (r"(\d+)\s*GB\s*RAM", "ram_gb"),
                (r"(\d+)\s*Go\s*RAM", "ram_gb"),
                (r"DDR(\d)", "ram_type")
            ],
            "display": [
                (r"(\d+[\.,]\d+)\"", "display_size"),
                (r"(\d+)\s*Hz", "refresh_rate"),
                (r"(4K|2K|FHD|HD)", "resolution")
            ],
            
            # Specificații telefoane
            "phone": [
                (r"(\d+)\s*MP", "camera_mp"),
                (r"(\d+)\s*mAh", "battery_mah"),
                (r"(5G|4G|LTE)", "network"),
                (r"Dual\s*SIM", "dual_sim")
            ],
            
            # Specificații laptopuri
            "laptop": [
                (r"i(\d)", "cpu_gen"),
                (r"(RTX|GTX)\s*(\d+)", "gpu"),
                (r"(SSD|HDD|NVMe)", "storage_type"),
                (r"Windows\s*(\d+)", "os_version")
            ]
        }

    def analyze_product_url(self, url: str) -> ProductAttributes:
        """
        Analizează un URL de produs și extrage atributele
        
        Args:
            url: URL-ul produsului
            
        Returns:
            ProductAttributes cu informațiile extrase
        """
        # Parsare URL
        parsed = urlparse(url)
        path = unquote(parsed.path)
        segments = [s for s in path.split('/') if s]
        
        # Inițializare atribute
        attrs = ProductAttributes()
        
        # Extrage categoria principală
        if segments:
            main_category = segments[0].lower()
            attrs.category = self._determine_category(main_category, segments)
            if len(segments) > 1:
                attrs.subcategory = self._determine_subcategory(attrs.category, segments[1])
        
        # Extrage brand și model din ultimul segment
        if segments:
            last_segment = segments[-1]
            brand, model = self._extract_brand_model(last_segment)
            attrs.brand = brand
            attrs.model = model
            
            # Extrage alte atribute din slug
            self._extract_attributes_from_slug(last_segment, attrs)
        
        return attrs
    
    def analyze_product_title(self, title: str, attrs: ProductAttributes = None) -> ProductAttributes:
        """
        Analizează titlul produsului pentru a extrage atribute suplimentare
        
        Args:
            title: Titlul produsului
            attrs: Opțional, atributele existente pentru actualizare
            
        Returns:
            ProductAttributes actualizat
        """
        if attrs is None:
            attrs = ProductAttributes()
            
        # Curăță titlul
        title = self._clean_title(title)
        
        # Extrage brand/model dacă nu sunt setate
        if not attrs.brand or not attrs.model:
            brand, model = self._extract_brand_model(title)
            if not attrs.brand:
                attrs.brand = brand
            if not attrs.model:
                attrs.model = model
        
        # Extrage specificații din titlu
        specs = self._extract_specs(title)
        attrs.specs.update(specs)
        
        # Extrage anul
        year_match = re.search(r'20(\d{2})', title)
        if year_match:
            attrs.year = 2000 + int(year_match.group(1))
            
        # Extrage culoarea
        color_match = re.search(r'(negru|alb|gri|albastru|rosu|roz|violet|gold|silver)', 
                              title.lower())
        if color_match:
            attrs.color = color_match.group(1).title()
            
        # Extrage capacitatea
        capacity_match = re.search(r'(\d+)\s*(GB|TB|Go)', title)
        if capacity_match:
            attrs.capacity = f"{capacity_match.group(1)}{capacity_match.group(2)}"
            
        return attrs
    
    def _clean_title(self, title: str) -> str:
        """Curăță și normalizează titlul produsului"""
        # Elimină spații multiple
        title = re.sub(r'\s+', ' ', title)
        
        # Elimină caractere speciale
        title = re.sub(r'[^\w\s\-.,()]', '', title)
        
        # Normalizează diacritice
        diacritics_map = {
            'ă': 'a', 'â': 'a', 'î': 'i',
            'ș': 's', 'ş': 's', 'ț': 't', 'ţ': 't'
        }
        for k, v in diacritics_map.items():
            title = title.replace(k, v)
            title = title.replace(k.upper(), v.upper())
            
        return title.strip()
    
    def _determine_category(self, main_category: str, segments: List[str]) -> str:
        """Determină categoria principală din URL"""
        # Verifică mai întâi dacă este o categorie de accesorii
        if main_category == "accesorii":
            return "phone_accessories"
            
        # Verifică potrivirea cu regulile de categorie
        for category, rules in self.category_rules.items():
            patterns = rules["patterns"]
            if any(re.search(pat, main_category, re.I) for pat in patterns):
                return category
                
        # Analiză euristică bazată pe toate segmentele
        path = " ".join(segments)
        scores = defaultdict(int)
        
        for category, rules in self.category_rules.items():
            for pattern in rules["patterns"]:
                matches = re.finditer(pattern, path, re.I)
                scores[category] += sum(1 for _ in matches)
                
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
            
        return "other"
    
    def _determine_subcategory(self, category: str, segment: str) -> Optional[str]:
        """Determină subcategoria bazată pe categoria principală și segment"""
        if category not in self.category_rules:
            return None
            
        rules = self.category_rules[category]
        if "subcategories" not in rules:
            return None
            
        # Verifică potrivirea cu subcategoriile
        for subcat, patterns in rules["subcategories"].items():
            if any(re.search(pat, segment, re.I) for pat in patterns):
                return subcat
                
        return None
    
    def _extract_brand_model(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrage brand și model din text"""
        text = text.lower()
        
        # Caută brand
        detected_brand = None
        for brand, patterns in self.brand_patterns.items():
            if any(re.search(pat, text, re.I) for pat in patterns):
                detected_brand = brand
                break
                
        # Extrage model
        model = None
        if detected_brand:
            # Elimină brandul din text pentru a găsi modelul
            for pattern in self.brand_patterns[detected_brand]:
                text = re.sub(pattern, '', text, flags=re.I)
                
        # Caută model în textul rămas
        model_patterns = [
            # Modele de telefoane
            r'([a-z]+(?:\s*\d+)?(?:\s*[a-z]*)?(?:\s*pro|\s*max|\s*ultra|\s*lite)?)',
            # Modele de laptopuri
            r'([a-z]+\d*(?:\s*\-?\d+[a-z]*)?)',
            # Modele generale
            r'([a-z\d]+(?:\-[a-z\d]+)*)'
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, text.strip())
            if match:
                model = match.group(1).strip()
                break
                
        return detected_brand, model
    
    def _extract_attributes_from_slug(self, slug: str, attrs: ProductAttributes) -> None:
        """Extrage atribute din slug-ul URL-ului"""
        # Extrage specificații
        specs = self._extract_specs(slug)
        attrs.specs.update(specs)
        
        # Caută serie (dacă există)
        series_patterns = [
            r'series\s*(\d+)',
            r'seria\s*(\d+)',
            r'([a-z]\d+)\s*series'
        ]
        
        for pattern in series_patterns:
            match = re.search(pattern, slug, re.I)
            if match:
                attrs.series = match.group(1)
                break
    
    def _extract_specs(self, text: str) -> Dict[str, str]:
        """Extrage specificații tehnice din text"""
        specs = {}
        
        # Aplică toate modelele de specificații
        for spec_type, patterns in self.spec_patterns.items():
            for pattern, key in patterns:
                matches = re.finditer(pattern, text, re.I)
                for match in matches:
                    if match.groups():
                        specs[key] = match.group(1)
                    else:
                        specs[key] = match.group(0)
                        
        return specs

    def analyze_price(self, price_text: str) -> Tuple[Optional[float], str]:
        """
        Analizează și normalizează textul prețului
        
        Args:
            price_text: Textul prețului (ex: "1299 lei", "1,299.99 MDL")
            
        Returns:
            Tuple (preț ca float, monedă)
        """
        if not price_text:
            return None, "MDL"
            
        # Curăță textul
        price_text = price_text.strip().lower()
        
        # Mapare monede
        currency_map = {
            'lei': 'MDL',
            'mdl': 'MDL',
            'eur': 'EUR',
            'euro': 'EUR',
            '€': 'EUR',
            'usd': 'USD',
            '$': 'USD'
        }
        
        # Extrage preț și monedă
        price_match = re.search(r'([\d,\.]+)\s*([a-zA-Z€$]+)?', price_text)
        if not price_match:
            return None, "MDL"
            
        # Procesează valoarea numerică
        try:
            price_str = price_match.group(1)
            price_str = price_str.replace(',', '')
            price = float(price_str)
        except (ValueError, AttributeError):
            return None, "MDL"
            
        # Determină moneda
        currency = "MDL"  # default
        if price_match.group(2):
            curr = price_match.group(2).lower()
            currency = currency_map.get(curr, "MDL")
            
        return price, currency