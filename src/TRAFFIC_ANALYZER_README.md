# Analiza Surselor de Trafic pentru Darwin.md

Acest modul extinde funcționalitatea scraper-ului Darwin.md pentru a analiza sursele de trafic ale site-ului. Cu ajutorul acestui modul, puteți obține informații valoroase despre canalele care aduc trafic pe site, referreri, cuvinte cheie din motoare de căutare, și analiza traficului provenit din rețele sociale.

## Funcționalități principale

### 1. Analiza referrer-ilor
- Identifică și analizează referer-urile acceptate și blocate
- Testează diverse referer-uri pentru a detecta potențiale blocări
- Generează statistici despre rata de acceptare a diferitelor referrer-uri

### 2. Analiza traficului din social media
- Detectează integrări cu rețele sociale (Facebook, Instagram, TikTok, etc.)
- Identifică butoanele de share și funcționalități de social media
- Generează rapoarte despre influența social media asupra traficului

### 3. Analiza traficului din motoare de căutare
- Extrage cuvinte cheie din URL-uri
- Identifică motoarele de căutare care aduc trafic
- Analizează distribuția traficului între diferitele motoare de căutare

### 4. Integrare cu API-uri externe
- SimilarWeb API pentru date despre trafic web
- SEMrush API pentru analiza cuvintelor cheie și trafic organic
- Integrare opțională cu alte surse de date

### 5. Vizualizări și rapoarte
- Generează grafice pentru sursele de trafic
- Exportă date în formate CSV și JSON
- Creează rapoarte HTML interactive

## Instalare

Asigurați-vă că aveți instalate toate dependențele necesare:

```bash
pip install requests pandas matplotlib python-dotenv
```

Pentru funcționalitatea completă, configurați cheile API în fișierul `.env`:

```
SEMRUSH_API_KEY=your_semrush_key_here
SIMILARWEB_API_KEY=your_similarweb_key_here
```

## Utilizare

### Analiză de bază

```python
from traffic_analyzer import TrafficAnalyzer

# Inițializează analizorul pentru domeniul dorit
analyzer = TrafficAnalyzer("darwin.md")

# Generează un raport complet
report = analyzer.generate_traffic_report()
print(f"Report saved to: {report.get('report_file')}")
```

### Analiza surselor de trafic din social media

```python
# Identifică și analizează sursele de trafic din social media
social_data = analyzer.identify_social_traffic_sources()

# Afișează platformele detectate
print("Detected social platforms:", social_data["found_platforms"])
print("Top platforms:", social_data["top_platforms"])
```

### Analiza traficului din motoare de căutare

```python
# Analizează traficul bazat pe sitemap
sitemap_data = analyzer.analyze_traffic_from_sitemap("https://darwin.md/sitemap.xml")

# Afișează cuvintele cheie top
print("Top search keywords:", sitemap_data["keyword_analysis"]["top_keywords"])
```

### Analiza referrer-ilor

```python
# Testează URL-urile cu diferite referreri
urls = ["https://darwin.md", "https://darwin.md/telefoane"]
referrer_data = analyzer.analyze_url_referrers(urls)

# Afișează referrerii acceptați și blocați
print("Top referrers:", referrer_data["top_referrers"])
print("Blocked referrers:", referrer_data["blocked_referrers"])
```

## Utilizarea Script-ului de Analiză

Pentru o analiză completă, puteți utiliza script-ul `analyze_darwin_traffic.py`:

```bash
# Analiză completă cu toate rapoartele
python analyze_darwin_traffic.py --domain darwin.md --full --visualize

# Doar analiză social media
python analyze_darwin_traffic.py --domain darwin.md --social

# Doar analiză căutări
python analyze_darwin_traffic.py --domain darwin.md --search

# Doar analiză referreri
python analyze_darwin_traffic.py --domain darwin.md --referrer
```

## Interpretarea Rezultatelor

Rapoartele generate oferă informații valoroase despre:

1. **Distribuția surselor de trafic**: Procentajul traficului venit din diferite canale (organic, direct, social, referral)
2. **Principalii referreri**: Site-urile care trimit cel mai mult trafic către darwin.md
3. **Cuvintele cheie principale**: Termenii de căutare care aduc utilizatori pe site
4. **Impactul social media**: Platformele sociale care generează cel mai mult trafic
5. **Detectarea blocărilor**: Identificarea surselor de trafic potențial blocate

## Integrare cu Darwin Scraper

Acest modul se integrează perfect cu restul funcționalităților Darwin Scraper:

```python
from darwin_scraper_complete import DarwinProductScraper
from traffic_analyzer import TrafficAnalyzer

# Inițializează scraper-ul și analizorul de trafic
scraper = DarwinProductScraper(openai_api_key="your_key")
analyzer = TrafficAnalyzer("darwin.md")

# Extrage produse
products_data = scraper.run_complete_extraction(max_products=100)

# Analizează traficul
traffic_report = analyzer.generate_traffic_report()

# Corelează datele pentru analiză avansată
print(f"Produse extrase: {len(products_data.get('products', []))}")
print(f"Raport trafic salvat în: {traffic_report.get('report_file')}")
```

## Limitări și Considerații

- Unele funcționalități necesită chei API externe (SEMrush, SimilarWeb)
- Analiza referrer-ilor este bazată pe simulări și poate să nu reflecte exact comportamentul real
- Funcțiile avansate pot necesita un număr mare de cereri HTTP și pot dura mai mult
- Pentru respectarea termenilor de utilizare ai site-ului, folosiți rate limiting și evitați suprasolicitarea serverelor

## Extensii viitoare

- Integrare cu Google Analytics API
- Analiza traficului mobil vs. desktop
- Heat-maps pentru interacțiuni pe pagină
- Corelarea datelor de trafic cu conversiile și vânzările