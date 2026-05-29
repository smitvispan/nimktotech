import re
import requests
import json
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def scrape_yellowpages_rajkot():
    results = []
    try:
        url = 'https://yellowpages.webindia123.com/d-py/Gujarat/Rajkot/Hardware-Fittings-And-Accessories-532/1/'
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for item in soup.select('table table tr'):
            text = item.get_text(' ', strip=True)
            if not text or len(text) < 5:
                continue
            name = ''
            for tag in item.select('b, strong, a[href*="Hardware"]'):
                t = tag.get_text(strip=True)
                if t and len(t) > 3 and t not in ('Write Review', 'Email', 'Website', 'Phone', 'Photos'):
                    name = t
                    break
            if name and 'Hardware' in name:
                address = ''
                for span in item.select('p, div, span'):
                    a = span.get_text(strip=True)
                    if 'Rajkot' in a:
                        address = a[:150]
                        break
                results.append({'name': name, 'address': address, 'source': 'YellowPages'})
    except Exception as e:
        print(f"[scraper] YellowPages error: {e}")

    unique = {}
    for r in results:
        key = r['name'].lower().strip()
        if key and key not in unique:
            unique[key] = r
    return list(unique.values())


def scrape_indiamart_rajkot():
    results = []
    try:
        url = 'https://dir.indiamart.com/rajkot/hardware.html'
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        seen = set()
        possible = soup.select('a[href*="rajkot"], a[href*="Hardware"], h2, h3, h4, strong')
        for el in possible:
            text = el.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 100 and 'hardware' in text.lower():
                if text.lower() not in seen:
                    seen.add(text.lower())
                    parent = el.find_parent('div', class_=True) or el.find_parent('li')
                    if parent:
                        results.append({'name': text, 'source': 'IndiaMart'})
    except Exception as e:
        print(f"[scraper] IndiaMart error: {e}")
    return results


def scrape_cybo():
    results = []
    try:
        url = 'https://www.cybo.com/IN/rajkot/hardware-store/'
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for link in soup.select('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if text and 'rajkot' in href.lower() and len(text) > 3:
                if any(k in text.lower() for k in ['hardware', 'store', 'shop']):
                    if text not in [r['name'] for r in results]:
                        results.append({'name': text, 'source': 'Cybo'})
                    elif len(results) > 20:
                        break
    except Exception as e:
        print(f"[scraper] Cybo error: {e}")
    return results


def scrape_google_search(query):
    results = []
    try:
        url = f'https://www.google.com/search?q={query}&num=20'
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for g in soup.select('.g'):
            title_el = g.select_one('h3')
            link_el = g.select_one('a')
            snippet_el = g.select_one('.VwiC3b, .lEBKkf, span.aCOpRe')
            if title_el:
                name = title_el.get_text(strip=True)
                link = link_el.get('href', '') if link_el else ''
                if '/url?q=' in link:
                    link = link.split('/url?q=')[1].split('&')[0]
                snippet = snippet_el.get_text(strip=True)[:200] if snippet_el else ''
                results.append({'name': name, 'website': link, 'snippet': snippet, 'source': 'Google'})
    except Exception as e:
        print(f"[scraper] Google error: {e}")
    return results


def live_search(location, category):
    term = f"{category} in {location}".replace(' ', '+')
    all_results = []

    all_results += scrape_yellowpages_rajkot()
    all_results += scrape_indiamart_rajkot()
    all_results += scrape_cybo()
    all_results += scrape_google_search(term)

    seen = set()
    unique = []
    for r in all_results:
        key = r.get('name', '').lower().strip()
        key = re.sub(r'[^a-z0-9]', '', key)
        if key and key not in seen and len(key) > 3:
            seen.add(key)
            if r.get('name', '').lower() not in ('write review', 'email', 'website', 'phone', 'photos',
                                                   'hardware fittings and accessories', 'computer hardware and consumables',
                                                   'upgrade to sponsored'):
                unique.append(r)

    return unique


if __name__ == '__main__':
    results = live_search('Rajkot', 'Hardware')
    print(json.dumps(results, indent=2))
    print(f"\nTotal: {len(results)} results")
