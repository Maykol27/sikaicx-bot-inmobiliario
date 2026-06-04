import asyncio
from scraper.fincaraiz import run_scraper
from scraper.metrocuadrado import run_metrocuadrado
from scraper.ciencuadras import run_ciencuadras
from utils.sheets import append_leads_to_sheet, get_existing_links, append_discarded_to_sheet

def main():
    print("Iniciando Bot Multi-Portal de Extraccion de Leads - SIKAI CX")
    nombre_hoja = "CGBI Leads Finca Raiz"
    
    existing_links = set()
    try:
        existing_links = get_existing_links(nombre_hoja)
        print(f"Se encontraron {len(existing_links)} propiedades ya registradas en Sheets.")
    except Exception as e:
        print(f"Aviso: No se pudieron leer los links existentes. {e}")
    
    leads_totales = []
    descartados_totales = []
    
    # 1. Finca Raíz
    try:
        print("\n--- Analizando Finca Raíz ---")
        leads_fr, desc_fr = asyncio.run(run_scraper(existing_links))
        leads_totales.extend(leads_fr)
        descartados_totales.extend(desc_fr)
    except Exception as e:
        print(f"Error en Finca Raiz: {e}")

    # 2. Metrocuadrado
    try:
        print("\n--- Analizando Metrocuadrado ---")
        leads_m2, desc_m2 = asyncio.run(run_metrocuadrado(existing_links))
        leads_totales.extend(leads_m2)
        descartados_totales.extend(desc_m2)
    except Exception as e:
        print(f"Error en Metrocuadrado: {e}")
        
    # 3. Ciencuadras
    try:
        print("\n--- Analizando Ciencuadras ---")
        leads_c100, desc_c100 = asyncio.run(run_ciencuadras(existing_links))
        leads_totales.extend(leads_c100)
        descartados_totales.extend(desc_c100)
    except Exception as e:
        print(f"Error en Ciencuadras: {e}")

    print(f"\nScraping finalizado.")
    print(f"Leads Válidos (Dueños Directos): {len(leads_totales)}")
    print(f"Leads Descartados (Inmobiliarias): {len(descartados_totales)}")
    
    # 2. Subir a Google Sheets
    if leads_totales:
        try:
            append_leads_to_sheet(nombre_hoja, leads_totales)
        except Exception as e:
            print(f"Error al guardar leads válidos: {e}")
    else:
        print("No se agregaron leads válidos hoy.")
        
    # 3. Guardar en Auditoría (Limitar a los primeros 50 para no desbordar el Sheets si hay miles)
    if descartados_totales:
        try:
            # Guardamos solo una muestra representativa (ej. primeros 100) para la auditoría
            append_discarded_to_sheet(nombre_hoja, descartados_totales[:100])
        except Exception as e:
            print(f"Error al guardar descartados: {e}")

if __name__ == "__main__":
    main()
