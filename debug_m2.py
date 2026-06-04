import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        print("Cargando Metrocuadrado...")
        await page.goto("https://www.metrocuadrado.com/apartamento-casa/venta/bogota/?precioDesde=600000000", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        html = await page.content()
        with open("metrocuadrado_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Cargando Ciencuadras...")
        await page.goto("https://www.ciencuadras.com/venta/bogota?price=600000000_20000000000", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        html = await page.content()
        with open("ciencuadras_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
