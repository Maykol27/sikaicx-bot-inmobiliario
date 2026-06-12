import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth(page)
        
        await page.goto("https://www.fincaraiz.com.co/venta/inmuebles/bogota?precio_minimo=600000000", timeout=60000)
        await asyncio.sleep(5)
        
        from bs4 import BeautifulSoup
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        tarjetas1 = soup.select("div.listingCard")
        tarjetas2 = soup.select("article.lc-card")
        tarjetas3 = soup.select("a[href*='/inmueble/'], a[href*='/apartamento-en-venta-']")
        
        print(f"Tarjetas div.listingCard: {len(tarjetas1)}")
        print(f"Tarjetas article.lc-card: {len(tarjetas2)}")
        print(f"Links de propiedades probables: {len(tarjetas3)}")
        
        await browser.close()

asyncio.run(test())
