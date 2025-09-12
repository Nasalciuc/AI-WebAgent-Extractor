import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

PRODUCT_INDICATORS = [
    '/telefoane/', '/laptopuri/', '/tablete/', '/accesorii/', '/audio/', '/gaming/',
    '/smart-home/', '/electronice/', '/produse/', '/product/', '/monitoare/', '/smartphone/',
    '/casti/', '/boxe/', '/sisteme-pc/', '/imprimante/', '/periferice-pc/', '/componente-pc/',
    '/camere-foto/', '/tehnica-bucatarie/', '/aspiratoare/', '/aparate-fitness/', '/transport-personal/',
    '/telefoane-mobile-cu-buton-', '/telefoane-dect-', '/sticle-si-folii-de-protectie-', '/cabluri-',
    '/incarcatoare-', '/huse-pentru-smartphone-', '/power-bank-', '/ceasuri-inteligente-',
    '/bratari-inteligente-', '/drone-', '/ochelari-vr-'
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; SitemapFetcher/1.0)'}


def parse_sitemap(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        # detect index
        sitems = root.findall('.//ns:sitemap', ns)
        if sitems:
            return 'index', [elem.find('ns:loc', ns).text for elem in sitems if elem.find('ns:loc', ns) is not None]
        # otherwise url set
        urls = [elem.find('ns:loc', ns).text for elem in root.findall('.//ns:url', ns) if elem.find('ns:loc', ns) is not None]
        return 'urls', urls
    except Exception as e:
        print(f'ERROR fetching {url}: {e}')
        return 'error', []


def is_product_url(u):
    if not u or not u.startswith('http'):
        return False
    ul = u.lower()
    if any(ind in ul for ind in PRODUCT_INDICATORS):
        return True
    # product id pattern
    import re
    if re.search(r'/\d+/?$', ul) or re.search(r'[?&]id=\d+', ul):
        return True
    return False


def main():
    root_sitemap = 'https://darwin.md/sitemap.xml'
    typ, items = parse_sitemap(root_sitemap)
    all_urls = []
    submaps = []
    if typ == 'index':
        submaps = items
        for sm in submaps:
            t, urls = parse_sitemap(sm)
            if t == 'urls':
                all_urls.extend(urls)
    elif typ == 'urls':
        all_urls = items
    else:
        # try robots.txt
        try:
            r = requests.get('https://darwin.md/robots.txt', headers=HEADERS, timeout=10)
            r.raise_for_status()
            s = r.text
            for line in s.splitlines():
                if line.lower().startswith('sitemap:'):
                    sm = line.split(':',1)[1].strip()
                    submaps.append(sm)
            for sm in submaps:
                t, urls = parse_sitemap(sm)
                if t == 'urls':
                    all_urls.extend(urls)
        except Exception as e:
            print('Failed robots.txt:', e)

    # dedupe and filter
    all_urls = list(dict.fromkeys(all_urls))
    product_urls = [u for u in all_urls if is_product_url(u)]

    print(f'Sub-sitemaps found: {len(submaps)}')
    print(f'Total URLs found: {len(all_urls)}')
    print(f'Product-like URLs: {len(product_urls)}')
    print('\nSample product URLs (up to 50):')
    for u in product_urls[:50]:
        print(u)


if __name__ == '__main__':
    main()
