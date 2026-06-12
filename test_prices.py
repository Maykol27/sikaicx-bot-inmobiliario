import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.fincaraiz.com.co/venta/inmuebles/bogota?precio_minimo=600000000", timeout=60000)
        await asyncio.sleep(2)
        
        from bs4 import BeautifulSoup
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        tarjetas = soup.select("article.lc-card")
        print(f"Tarjetas encontradas: {len(tarjetas)}")
        
        for t in tarjetas[:5]:
            precio_element = t.select_one("p.main-price")
            precio = precio_element.text.strip() if precio_element else "Desconocido"
            print(f"Precio crudo: {precio}")
            
        await browser.close()

asyncio.run(test())
