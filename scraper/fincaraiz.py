import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime

# URLs base de búsqueda (Primera página)
URL_VENTAS_BOGOTA = "https://www.fincaraiz.com.co/venta/inmuebles/bogota?precio_minimo=600000000"
URL_ARRIENDOS_BOGOTA = "https://www.fincaraiz.com.co/arriendo/inmuebles/bogota?precio_minimo=3000000"

MAX_PAGINAS = 25  # Aprox 525 propiedades

def cumple_precio_minimo(precio_str, tipo):
    if not precio_str or precio_str == "Desconocido":
        return True
    numeros = re.sub(r'[^\d]', '', precio_str)
    if not numeros:
        return True
    p = int(numeros)
    if tipo == "Venta" and p < 600000000:
        return False
    if tipo == "Arriendo" and p < 3000000:
        return False
    return True

def es_dueno_directo(descripcion, anunciante_nombre=""):
    """
    Usa heurísticas estrictas para determinar si la publicación es de un dueño directo.
    """
    descripcion = descripcion.lower()
    anunciante = anunciante_nombre.lower()
    
    # Lista masiva de empresas, agencias y startups (Proptechs)
    palabras_inmobiliaria = [
        "inmobiliaria", "bienes raices", "constructora", "propiedades", 
        "realty", "brokers", "agencia", "sas", "s.a.s", "inversiones", 
        "grupo", "asesor", "soluciones", "habitat", "capital", "renta", 
        "house", "home", "century 21", "remax", "coldwell", "corredor",
        "houm", "habi", "aptuno", "la haus", "cuadras", "pad", "inmuebles",
        "bienes", "raices", "asociados", "ltda", "vivienda", "real estate",
        "marval", "amarilo", "cusezar", "bolivar", "apiros", "ospinas", "ar",
        "proyecto", "constructores", "edificadora", "inmueble"
    ]
    for p in palabras_inmobiliaria:
        if re.search(r'\b' + re.escape(p) + r'\b', anunciante):
            return (False, f"Nombre de empresa/inmobiliaria detectado: '{p}'")
            
    # Filtro de Persona Natural:
    # Si el nombre del anunciante tiene números (ej. "Houm 123"), descartar.
    if re.search(r'\d', anunciante):
        return (False, "El nombre del anunciante contiene números")
        
    # Palabras clave fuertes de dueño directo
    palabras_directo = ["venta directa", "sin intermediarios", "motivo viaje", "dueño directo", "trato directo", "directamente", "vendo mi"]
    for p in palabras_directo:
        if p in descripcion:
            return (True, f"Palabra clave de dueño directo: '{p}'")
            
    # Palabras que suelen usar las inmobiliarias en la descripción
    palabras_agencia_desc = [
        "asesor", "agendar cita", "nuestra", "comisión", "código", "cod:", "ref:", 
        "inmobiliarios", "gestionamos", "te ayudamos", "somos una", "nuestro equipo",
        "contáctanos para", "tramitamos tu crédito", "visita nuestra", "inmueble destacado"
    ]
    for p in palabras_agencia_desc:
        if p in descripcion:
            return (False, f"Palabra de agencia en descripción: '{p}'")
            
    # Heurística extra: Las agencias suelen poner descripciones muy largas o usar mayúsculas sostenidas
    # Por ahora, dejemos que retorne False por defecto a menos que tenga "Dueño directo" 
    # o si la descripción es muy corta y personal.
    if len(descripcion) < 150: 
        return (True, "Descripción corta típica de persona natural")
        
    return (False, "Descartado por defecto (No cumple perfil estricto de dueño)")

async def extract_listings_from_pages(page, base_url, tipo, existing_links):
    """
    Navega por múltiples páginas, extrae los listings, ignora duplicados y filtra dueños directos.
    """
    leads_validos = []
    leads_descartados = []
    
    for page_num in range(1, MAX_PAGINAS + 1):
        # Finca Raíz maneja paginación con el parámetro &pagina=N
        url_paginada = base_url if page_num == 1 else f"{base_url}&pagina={page_num}"
        print(f"Navegando a: {url_paginada}")
        
        await page.goto(url_paginada, wait_until="networkidle")
        
        # Hacemos scroll para cargar más elementos si hay lazy loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3000) 
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Los selectores reales de Finca Raiz
        tarjetas = soup.select("div.listingCard")
        
        if not tarjetas:
            print(f"No se encontraron más tarjetas en la página {page_num}. Terminando paginación.")
            break
            
        print(f"Página {page_num}: Se encontraron {len(tarjetas)} tarjetas.")
        
        for tarjeta in tarjetas:
            try:
                link_tag = tarjeta.select_one("a.lc-data")
                if not link_tag: continue
                
                link = "https://www.fincaraiz.com.co" + link_tag.get("href", "")
                
                # ANTIDUPLICIDAD: Si ya existe en la hoja, lo saltamos inmediatamente
                if link in existing_links:
                    continue
                
                desc_element = tarjeta.select_one("p.lc-description")
                descripcion = desc_element.text.strip() if desc_element else ""
                
                anunciante_element = tarjeta.select_one("div.lc-owner-name")
                anunciante = anunciante_element.text.strip() if anunciante_element else ""
                
                precio_element = tarjeta.select_one("p.main-price")
                precio = precio_element.text.strip() if precio_element else "Desconocido"
                
                # Descartar inmediatamente si no cumple el precio (ej. propiedades promocionadas o basura)
                if not cumple_precio_minimo(precio, tipo):
                    continue
                
                ubicacion_element = tarjeta.select_one("strong.lc-location")
                ubicacion = ubicacion_element.text.strip() if ubicacion_element else "Bogotá"
                
                is_directo, razon = es_dueno_directo(descripcion, anunciante)
                
                lead_data = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d"),
                    "Tipo": tipo,
                    "Precio": precio,
                    "Ubicación": ubicacion,
                    "Link": link,
                    "Teléfono": "Por implementar",
                    "Descripción": descripcion[:200] + "...", 
                    "Estado": razon
                }
                
                if is_directo:
                    leads_validos.append(lead_data)
                    print(f"Lead directo encontrado: {link}")
                else:
                    leads_descartados.append(lead_data)
                
                existing_links.add(link) 
                    
            except Exception as e:
                print(f"Error procesando tarjeta: {e}")
                continue
                
        # Pausa entre páginas para no ser bloqueados
        await page.wait_for_timeout(2000)

    return leads_validos, leads_descartados

async def run_scraper(existing_links):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        todos_validos = []
        todos_descartados = []
        
        print("Iniciando scraping de Ventas...")
        validos, descartados = await extract_listings_from_pages(page, URL_VENTAS_BOGOTA, "Venta", existing_links)
        todos_validos.extend(validos)
        todos_descartados.extend(descartados)
        
        print("Iniciando scraping de Arriendos...")
        validos, descartados = await extract_listings_from_pages(page, URL_ARRIENDOS_BOGOTA, "Arriendo", existing_links)
        todos_validos.extend(validos)
        todos_descartados.extend(descartados)
        
        await browser.close()
        return todos_validos, todos_descartados
