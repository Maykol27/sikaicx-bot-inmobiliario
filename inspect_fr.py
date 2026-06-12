import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.fincaraiz.com.co/venta/inmuebles/bogota?precio_minimo=600000000", timeout=60000)
        await asyncio.sleep(3)
        
        from bs4 import BeautifulSoup
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Encuentra las tarjetas de propiedades buscando div o article con href
        for link in soup.find_all('a', href=True):
            if "venta-en-" in link['href'] or "arriendo-en-" in link['href']:
                parent = link.parent
                if parent:
                    print(f"Parent tag: {parent.name}, class: {parent.get('class')}")
                    # Buscar precio dentro de parent
                    print(f"Text: {parent.get_text(strip=True)[:100]}")
                    break
        
        await browser.close()

asyncio.run(inspect())
