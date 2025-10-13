#!/usr/bin/env python3
"""
Script pentru analiza și vizualizarea surselor de trafic pentru Darwin.md
Utilizează modulul traffic_analyzer pentru a genera un raport complet despre sursele de trafic.
"""

import argparse
import json
import logging
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

from traffic_analyzer import TrafficAnalyzer

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_analysis.log'),
        logging.StreamHandler()
    ]
)

# Încărcăm variabilele de mediu
load_dotenv()

def visualize_traffic_sources(data, output_file=None):
    """
    Vizualizează sursele de trafic într-un grafic
    
    Args:
        data: Dicționar cu sursele de trafic și procentaje
        output_file: Fișierul pentru salvarea graficului
    """
    sources = []
    percentages = []
    
    for source, percentage in data.items():
        if isinstance(percentage, (int, float)):
            sources.append(source)
            percentages.append(percentage)
    
    if not sources:
        logging.error("No traffic source data available for visualization")
        return
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(sources, percentages, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'])
    
    # Adaugă etichete și titlu
    plt.title('Surse de Trafic pentru Darwin.md', fontsize=16)
    plt.xlabel('Sursa', fontsize=12)
    plt.ylabel('Procentaj (%)', fontsize=12)
    plt.xticks(rotation=45)
    
    # Adaugă valori deasupra barelor
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
        logging.info(f"Chart saved to {output_file}")
    else:
        plt.show()

def create_social_media_analysis(analyzer, output_dir):
    """
    Analizează și generează raport despre traficul din social media
    
    Args:
        analyzer: Instanța TrafficAnalyzer
        output_dir: Directorul pentru output
        
    Returns:
        Path către fișierul HTML generat
    """
    social_data = analyzer.identify_social_traffic_sources(sample_pages=20)
    
    # Generează un HTML cu rezultatele
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(output_dir, f"social_media_report_{timestamp}.html")
    
    # Pregătim datele pentru vizualizare
    platforms = list(social_data["integration_count"].keys())
    integration_counts = list(social_data["integration_count"].values())
    share_counts = list(social_data["share_buttons"].values())
    
    # Creăm un DataFrame pentru un tabel HTML
    df = pd.DataFrame({
        "Platform": platforms,
        "Integration Count": integration_counts,
        "Share Buttons": share_counts
    })
    df = df.sort_values("Integration Count", ascending=False)
    
    # Generăm HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Social Media Traffic Analysis for {analyzer.target_domain}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #2c3e50; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .summary {{ background-color: #eef; padding: 15px; border-radius: 5px; }}
            .chart {{ margin: 30px 0; max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Social Media Traffic Analysis</h1>
            <h2>Domain: {analyzer.target_domain}</h2>
            <p>Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="summary">
                <h3>Summary</h3>
                <p><strong>URLs analyzed:</strong> {social_data["urls_analyzed"]}</p>
                <p><strong>Social platforms found:</strong> {", ".join(social_data["found_platforms"])}</p>
                <p><strong>Top platforms:</strong> {", ".join([p[0] for p in social_data["top_platforms"][:3]])}</p>
            </div>
            
            <h3>Social Platform Integration</h3>
            {df.to_html(index=False)}
            
            <div class="chart">
                <h3>Platform Integration Chart</h3>
                <img src="data:image/png;base64,{generate_chart_base64(df)}" alt="Social Media Chart">
            </div>
            
            <h3>Recommendations</h3>
            <ul>
                <li>Focus on top platforms: {", ".join([p[0] for p in social_data["top_platforms"][:2]])}</li>
                <li>Add more share buttons to increase social visibility</li>
                <li>Consider adding {get_missing_popular_platforms(social_data["found_platforms"])} integration</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Salvăm HTML-ul
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logging.info(f"Social media report saved to {html_file}")
    return html_file

def generate_chart_base64(df):
    """Generează un chart și îl convertește în base64 pentru includere în HTML"""
    import io
    import base64
    
    plt.figure(figsize=(10, 6))
    plt.bar(df['Platform'], df['Integration Count'], label='Integration Count')
    plt.bar(df['Platform'], df['Share Buttons'], bottom=df['Integration Count'], 
            label='Share Buttons', alpha=0.7)
    plt.xlabel('Platform')
    plt.ylabel('Count')
    plt.title('Social Media Integration Analysis')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Salvăm în buffer și convertim în base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def get_missing_popular_platforms(found_platforms):
    """Returnează platforme populare care lipsesc"""
    popular_platforms = ['facebook', 'instagram', 'tiktok', 'twitter', 'youtube']
    missing = [p for p in popular_platforms if p not in found_platforms]
    if missing:
        return ", ".join(missing)
    return "all major platforms are integrated"

def analyze_search_traffic(analyzer, output_dir):
    """
    Analizează și generează raport despre traficul din căutări
    
    Args:
        analyzer: Instanța TrafficAnalyzer
        output_dir: Directorul pentru output
        
    Returns:
        Path către fișierul cu raportul
    """
    # Obținem sitemap-ul pentru analiză
    sitemap_url = f"https://{analyzer.target_domain}/sitemap.xml"
    result = analyzer.analyze_traffic_from_sitemap(sitemap_url)
    
    if not result.get("success"):
        logging.error(f"Error analyzing sitemap: {result.get('error')}")
        return None
    
    # Extragem analiza de cuvinte cheie
    keyword_analysis = result.get("keyword_analysis", {})
    top_keywords = keyword_analysis.get("top_keywords", {})
    
    # Creăm un CSV cu rezultatele
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(output_dir, f"search_keywords_{timestamp}.csv")
    
    if top_keywords:
        df = pd.DataFrame([
            {"Keyword": keyword, "Count": count}
            for keyword, count in top_keywords.items()
        ])
        df.to_csv(csv_file, index=False)
        logging.info(f"Search keyword report saved to {csv_file}")
    
    # Generăm un raport mai detaliat în JSON
    json_file = os.path.join(output_dir, f"search_traffic_{timestamp}.json")
    
    search_report = {
        "domain": analyzer.target_domain,
        "date": datetime.now().isoformat(),
        "analyzed_urls": result.get("analyzed_urls"),
        "urls_with_keywords": keyword_analysis.get("urls_with_keywords"),
        "top_keywords": top_keywords,
        "search_engines": keyword_analysis.get("search_engines", {}),
        "keyword_details": keyword_analysis.get("keyword_details", [])[:20]  # Limităm la primele 20
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(search_report, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Search traffic report saved to {json_file}")
    return json_file

def main():
    parser = argparse.ArgumentParser(description="Darwin Traffic Analysis Tool")
    parser.add_argument("--domain", type=str, default="darwin.md", help="Domain to analyze")
    parser.add_argument("--output", type=str, default="reports", help="Output directory for reports")
    parser.add_argument("--full", action="store_true", help="Generate full comprehensive report")
    parser.add_argument("--social", action="store_true", help="Generate social media traffic analysis")
    parser.add_argument("--search", action="store_true", help="Generate search traffic analysis")
    parser.add_argument("--referrer", action="store_true", help="Generate referrer traffic analysis")
    parser.add_argument("--visualize", action="store_true", help="Generate visualizations")
    
    args = parser.parse_args()
    
    # Creăm directorul de output dacă nu există
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    print(f"=== Darwin Traffic Analysis Tool ===")
    print(f"Analyzing domain: {args.domain}")
    
    # Inițializăm analizorul
    analyzer = TrafficAnalyzer(args.domain)
    
    # Generăm rapoartele solicitate
    if args.social or args.full:
        print("Generating social media traffic analysis...")
        social_report = create_social_media_analysis(analyzer, args.output)
        if social_report:
            print(f"Social media report saved to: {social_report}")
    
    if args.search or args.full:
        print("Generating search traffic analysis...")
        search_report = analyze_search_traffic(analyzer, args.output)
        if search_report:
            print(f"Search traffic report saved to: {search_report}")
    
    if args.referrer or args.full:
        print("Analyzing referrer traffic...")
        # Obținem câteva URL-uri pentru testare
        sitemap_url = f"https://{args.domain}/sitemap.xml"
        sitemap_data = analyzer.analyze_traffic_from_sitemap(sitemap_url)
        
        if sitemap_data.get("success"):
            sample_urls = sitemap_data.get("url_categories", {}).get("categories", [])[:5]
            sample_urls += sitemap_data.get("url_categories", {}).get("products", [])[:5]
            
            if sample_urls:
                referrer_data = analyzer.analyze_url_referrers(sample_urls)
                
                # Salvăm rezultatele
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_file = os.path.join(args.output, f"referrer_analysis_{timestamp}.json")
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(referrer_data, f, ensure_ascii=False, indent=2)
                
                print(f"Referrer analysis saved to: {json_file}")
    
    # Generăm raportul complet
    if args.full:
        print("Generating comprehensive traffic report...")
        report_result = analyzer.generate_traffic_report(args.output)
        
        if report_result.get("success"):
            print(f"Full traffic report saved to: {report_result.get('report_file')}")
            
            # Vizualizăm sursele de trafic
            if args.visualize and report_result.get("chart_file"):
                print(f"Traffic visualization saved to: {report_result.get('chart_file')}")
    
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()