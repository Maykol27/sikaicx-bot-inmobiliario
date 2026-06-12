import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

def check_fr():
    print("--- FINCA RAIZ ---")
    res = requests.get("https://www.fincaraiz.com.co/venta/inmuebles/bogota?precio_minimo=600000000", headers=headers)
    print(f"FR Status: {res.status_code}")
    soup = BeautifulSoup(res.text, 'html.parser')
    cards = soup.select("article.lc-card")
    print(f"Cards found (article.lc-card): {len(cards)}")
    if len(cards) == 0:
        # try to find anything that looks like a card
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        if "Access denied" in res.text or "Cloudflare" in res.text:
            print("BLOCKED BY CLOUDFLARE/DATADOME")

def check_c100():
    print("\n--- CIENCUADRAS ---")
    res = requests.get("https://www.ciencuadras.com/inmueble/venta-apartamento-bogota-cedritos-3-habitaciones-2-banos-1-garajes/7565403", headers=headers)
    print(f"C100 Status: {res.status_code}")
    soup = BeautifulSoup(res.text, 'html.parser')
    # Try to find description
    desc = soup.select_one("div.description-container, div.property-description, p.description")
    if desc:
        print(f"Found desc class: {desc.get('class')}")
    else:
        # look for any div with a lot of text
        for d in soup.find_all('div'):
            if len(d.get_text(strip=True)) > 200:
                print(f"Possible desc div class: {d.get('class')}")
                break

def check_m2():
    print("\n--- METROCUADRADO ---")
    res = requests.get("https://www.metrocuadrado.com/inmueble/venta-apartamento-bogota-cedritos-3-habitaciones-2-banos-1-garajes/123456", headers=headers)
    print(f"M2 Status: {res.status_code}")
    # just print status, we know M2 works but we need description selector

check_fr()
check_c100()
