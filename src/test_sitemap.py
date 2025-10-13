import requests
import xml.etree.ElementTree as ET

def test_sitemap():
    url = "https://darwin.md/sitemap.xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Get all URLs from sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('.//ns:url/ns:loc', namespace)
        sitemaps = root.findall('.//ns:sitemap/ns:loc', namespace)
        
        print(f"Found {len(urls)} URLs and {len(sitemaps)} sitemaps")
        
        # Print first few URLs as sample
        print("\nSample URLs:")
        for url in urls[:5]:
            print(url.text)
            
        print("\nSitemaps found:")
        for sitemap in sitemaps:
            print(sitemap.text)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_sitemap()