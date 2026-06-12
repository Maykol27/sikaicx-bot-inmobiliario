import asyncio
import re
from playwright.async_api import async_playwright
from utils.sheets import get_sheets_client, get_existing_links, append_leads_to_sheet
from scraper.fincaraiz import es_dueno_directo

async def rescue():
    client = get_sheets_client()
    sheet_audit = client.open("CGBI Leads Finca Raiz").worksheet("Auditoría")
    data = sheet_audit.get_all_values()
    
    # Filtrar descartados de Finca Raiz y M2 por "ar"
    sospechosos = [row for row in data if row[0] == '2026-06-05' and "'ar'" in row[5]]
    print(f"Total a re-evaluar: {len(sospechosos)}")
    
    # Obtener links ya existentes en Hoja 1 para no duplicar
    existing_links = get_existing_links("CGBI Leads Finca Raiz")
    
    leads_rescatados = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        for i, s in enumerate(sospechosos):
            fecha, tipo, precio, ubicacion, link, razon = s
            if link in existing_links:
                continue
                
            try:
                await page.goto(link, timeout=20000)
                await asyncio.sleep(1) # wait for render
                
                texto_pagina = await page.evaluate('document.body.innerText')
                # Intentar buscar anunciante especifico si es Finca Raiz
                anunciante = ""
                if "fincaraiz.com.co" in link:
                    # En Finca Raiz el anunciante suele estar en un div de contacto
                    anun_element = await page.query_selector('p.name')
                    if anun_element:
                        anunciante = await anun_element.inner_text()
                elif "metrocuadrado.com" in link:
                    anun_element = await page.query_selector('h3.contact-name, div.contact-name')
                    if anun_element:
                        anunciante = await anun_element.inner_text()
                
                # Re-evaluar con el motor corregido
                is_directo, nueva_razon = es_dueno_directo(texto_pagina, anunciante)
                
                if is_directo:
                    print(f"¡RESCATADO! {link} (Anunciante: {anunciante})")
                    leads_rescatados.append({
                        "Fecha": "2026-06-06", # Fecha de rescate
                        "Tipo": tipo,
                        "Precio": precio,
                        "Ubicación": ubicacion,
                        "Link": link,
                        "Teléfono": "Por implementar",
                        "Descripción": texto_pagina[:150].replace('\n', ' ') + "...",
                        "Estado": "Rescatado post-auditoría"
                    })
                    existing_links.add(link)
                
                # Imprimir progreso cada 10
                if (i+1) % 10 == 0:
                    print(f"Progreso: {i+1}/{len(sospechosos)}")
                    
            except Exception as e:
                print(f"Error cargando {link}: {e}")
                
        await browser.close()
        
    print(f"\nFinalizado. Total rescatados: {len(leads_rescatados)}")
    if leads_rescatados:
        append_leads_to_sheet("CGBI Leads Finca Raiz", leads_rescatados)
        print("¡Guardados exitosamente en Hoja 1!")

asyncio.run(rescue())
