import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        print("Cargando Finca Raiz...")
        await page.goto("https://www.fincaraiz.com.co/venta/inmuebles/bogota?precio_minimo=600000000", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        html = await page.content()
        with open("fincaraiz_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML guardado en fincaraiz_debug.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
