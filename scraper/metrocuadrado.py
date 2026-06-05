import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime
from scraper.fincaraiz import es_dueno_directo, cumple_precio_minimo

URL_VENTAS = "https://www.metrocuadrado.com/apartamento-casa/venta/bogota/?precioDesde=600000000"
URL_ARRIENDOS = "https://www.metrocuadrado.com/apartamento-casa/arriendo/bogota/?precioDesde=3000000"
MAX_PAGINAS = 30

async def extract_metrocuadrado(page, base_url, tipo, existing_links):
    leads_validos = []
    leads_descartados = []
    
    for page_num in range(1, MAX_PAGINAS + 1):
        # Metrocuadrado paginación (ej: &pagina=2)
        url = f"{base_url}&pagina={page_num}" if page_num > 1 else base_url
        print(f"[M2] Navegando a: {url}")
        
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        links = [l['href'] for l in soup.find_all("a", href=True) if '/inmueble/' in l['href']]
        links = list(set(links)) # Deduplicar en la página
        
        if not links:
            print(f"[M2] No se encontraron más tarjetas en página {page_num}.")
            break
            
        print(f"[M2] Página {page_num}: {len(links)} links encontrados.")
        
        for href in links:
            full_link = "https://www.metrocuadrado.com" + href if href.startswith("/") else href
            
            if full_link in existing_links:
                continue
                
            existing_links.add(full_link)
            
            try:
                # Visit the actual listing
                nuevo_contexto = await page.context.new_page()
                await nuevo_contexto.goto(full_link, wait_until="domcontentloaded", timeout=15000)
                await nuevo_contexto.wait_for_timeout(2000)
                
                texto_pagina = await nuevo_contexto.evaluate("document.body.innerText")
                await nuevo_contexto.close()
                
                # Extraer precio con regex básico
                precio_match = re.search(r'\$([\d\.]+)', texto_pagina)
                precio = f"${precio_match.group(1)}" if precio_match else "Desconocido"
                
                # Descartar inmediatamente si no cumple el precio
                if not cumple_precio_minimo(precio, tipo):
                    continue
                
                # Usamos el texto completo para pasar por nuestra heurística estricta
                is_directo, razon = es_dueno_directo(texto_pagina, texto_pagina[:100])
                
                lead_data = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d"),
                    "Tipo": tipo,
                    "Precio": precio,
                    "Ubicación": "Bogotá (M2)",
                    "Link": full_link,
                    "Teléfono": "Por implementar",
                    "Descripción": "Extraído de M2...",
                    "Estado": razon
                }
                
                if is_directo:
                    leads_validos.append(lead_data)
                    print(f"🎯 [M2] Lead directo encontrado: {full_link}")
                else:
                    leads_descartados.append(lead_data)
            except Exception as e:
                print(f"[M2] Error al visitar link: {e}")
                
    return leads_validos, leads_descartados

async def run_metrocuadrado(existing_links):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        todos_validos = []
        todos_descartados = []
        print("Iniciando M2 Ventas...")
        v, d = await extract_metrocuadrado(page, URL_VENTAS, "Venta", existing_links)
        todos_validos.extend(v)
        todos_descartados.extend(d)
        
        print("Iniciando M2 Arriendos...")
        v, d = await extract_metrocuadrado(page, URL_ARRIENDOS, "Arriendo", existing_links)
        todos_validos.extend(v)
        todos_descartados.extend(d)
        
        await browser.close()
        return todos_validos, todos_descartados
