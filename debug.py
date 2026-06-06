import asyncio
from scraper.fincaraiz import extract_listings_from_pages, URL_VENTAS_BOGOTA
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        print("Testing Finca Raiz Venta...")
        
        # Override max paginas for fast test
        import scraper.fincaraiz
        scraper.fincaraiz.MAX_PAGINAS = 1
        
        v, d = await extract_listings_from_pages(page, URL_VENTAS_BOGOTA, "Venta", set())
        print(f"Validos: {len(v)}")
        print(f"Descartados: {len(d)}")
        if d:
            print(f"Sample descartado: {d[0]}")
        await browser.close()

asyncio.run(debug())
