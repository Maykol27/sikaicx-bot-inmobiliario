import asyncio
from playwright.async_api import async_playwright
from scraper.fincaraiz import extract_listings_from_pages, URL_VENTAS_BOGOTA
import scraper.fincaraiz

from scraper.metrocuadrado import run_metrocuadrado
import scraper.metrocuadrado

from scraper.ciencuadras import run_ciencuadras
import scraper.ciencuadras

async def test_fr():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        scraper.fincaraiz.MAX_PAGINAS = 1
        print("Testing Finca Raiz Venta...")
        v, d = await extract_listings_from_pages(page, URL_VENTAS_BOGOTA, "Venta", set())
        print(f"FR Validos: {len(v)}, Descartados: {len(d)}")
        await browser.close()

async def test_m2():
    scraper.metrocuadrado.MAX_PAGINAS = 1
    v, d = await run_metrocuadrado(set())
    print(f"M2 Validos: {len(v)}, Descartados: {len(d)}")

async def test_c100():
    scraper.ciencuadras.MAX_PAGINAS = 1
    v, d = await run_ciencuadras(set())
    print(f"C100 Validos: {len(v)}, Descartados: {len(d)}")

async def diag():
    print("--- DIAGNOSTICO ---")
    try:
        await test_fr()
    except Exception as e:
        print(f"FR Error: {e}")
        
    try:
        await test_m2()
    except Exception as e:
        print(f"M2 Error: {e}")
        
    try:
        await test_c100()
    except Exception as e:
        print(f"C100 Error: {e}")

asyncio.run(diag())
