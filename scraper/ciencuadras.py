import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime
from scraper.fincaraiz import es_dueno_directo

URL_VENTAS = "https://www.ciencuadras.com/venta/bogota?price=600000000_20000000000"
URL_ARRIENDOS = "https://www.ciencuadras.com/arriendo/bogota?price=3000000_50000000"
MAX_PAGINAS = 5

async def extract_ciencuadras(page, base_url, tipo, existing_links):
    leads = []
    
    for page_num in range(1, MAX_PAGINAS + 1):
        # Ciencuadras paginación (ej: &page=2)
        url = f"{base_url}&page={page_num}" if page_num > 1 else base_url
        print(f"[C100] Navegando a: {url}")
        
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(4000)
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        links = [l['href'] for l in soup.find_all("a", href=True) if '/inmueble/' in l['href']]
        links = list(set(links))
        
        if not links:
            print(f"[C100] No se encontraron más tarjetas en página {page_num}.")
            break
            
        print(f"[C100] Página {page_num}: {len(links)} links encontrados.")
        
        for href in links:
            full_link = "https://www.ciencuadras.com" + href if href.startswith("/") else href
            
            if full_link in existing_links:
                continue
                
            existing_links.add(full_link)
            
            try:
                nuevo_contexto = await page.context.new_page()
                await nuevo_contexto.goto(full_link, wait_until="domcontentloaded", timeout=15000)
                await nuevo_contexto.wait_for_timeout(2000)
                
                texto_pagina = await nuevo_contexto.evaluate("document.body.innerText")
                await nuevo_contexto.close()
                
                precio_match = re.search(r'\$([\d\.]+)', texto_pagina)
                precio = f"${precio_match.group(1)}" if precio_match else "Desconocido"
                
                if es_dueno_directo(texto_pagina, texto_pagina[:100]): 
                    lead = {
                        "Fecha": datetime.now().strftime("%Y-%m-%d"),
                        "Tipo": tipo,
                        "Precio": precio,
                        "Ubicación": "Bogotá (C100)",
                        "Link": full_link,
                        "Teléfono": "Por implementar",
                        "Descripción": "Extraído de C100...",
                        "Estado": ""
                    }
                    leads.append(lead)
                    print(f"🎯 [C100] Lead directo encontrado: {full_link}")
            except Exception as e:
                print(f"[C100] Error al visitar link: {e}")
                
    return leads

async def run_ciencuadras(existing_links):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        todos = []
        print("Iniciando C100 Ventas...")
        todos.extend(await extract_ciencuadras(page, URL_VENTAS, "Venta", existing_links))
        print("Iniciando C100 Arriendos...")
        todos.extend(await extract_ciencuadras(page, URL_ARRIENDOS, "Arriendo", existing_links))
        
        await browser.close()
        return todos
