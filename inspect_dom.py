import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Ciencuadras
        print("Ciencuadras...")
        await page.goto("https://www.ciencuadras.com/venta/bogota?price=600000000_20000000000", timeout=60000)
        await asyncio.sleep(2)
        # Get first link
        links = await page.query_selector_all('a[href*="/inmueble/"]')
        if links:
            href = await links[0].get_attribute('href')
            full_url = "https://www.ciencuadras.com" + href if not href.startswith('http') else href
            await page.goto(full_url, timeout=60000)
            await asyncio.sleep(2)
            
            # Print body structure
            html = await page.content()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            # Find elements with large text
            for p_tag in soup.find_all(['p', 'div']):
                text = p_tag.get_text(strip=True)
                if len(text) > 200:
                    print(f"C100 Class: {p_tag.get('class')}")
                    print(f"C100 Text: {text[:100]}...")
                    break
        
        # Metrocuadrado
        print("\nMetrocuadrado...")
        await page.goto("https://www.metrocuadrado.com/apartamento-casa/venta/bogota/?precioDesde=600000000", timeout=60000)
        await asyncio.sleep(2)
        links = await page.query_selector_all('a[href*="/inmueble/"]')
        if links:
            href = await links[0].get_attribute('href')
            full_url = "https://www.metrocuadrado.com" + href if not href.startswith('http') else href
            await page.goto(full_url, timeout=60000)
            await asyncio.sleep(2)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            for p_tag in soup.find_all(['p', 'div', 'span']):
                text = p_tag.get_text(strip=True)
                if len(text) > 200:
                    print(f"M2 Class: {p_tag.get('class')}")
                    print(f"M2 Text: {text[:100]}...")
                    break
                    
        await browser.close()

asyncio.run(inspect())
