import asyncio
from scraper.fincaraiz import run_scraper
from scraper.metrocuadrado import run_metrocuadrado
from scraper.ciencuadras import run_ciencuadras
from utils.sheets import append_leads_to_sheet, get_existing_links

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
    
    # 1. Finca Raíz
    try:
        print("\n--- Analizando Finca Raíz ---")
        leads_fr = asyncio.run(run_scraper(existing_links))
        leads_totales.extend(leads_fr)
    except Exception as e:
        print(f"Error en Finca Raiz: {e}")

    # 2. Metrocuadrado
    try:
        print("\n--- Analizando Metrocuadrado ---")
        leads_m2 = asyncio.run(run_metrocuadrado(existing_links))
        leads_totales.extend(leads_m2)
    except Exception as e:
        print(f"Error en Metrocuadrado: {e}")
        
    # 3. Ciencuadras
    try:
        print("\n--- Analizando Ciencuadras ---")
        leads_c100 = asyncio.run(run_ciencuadras(existing_links))
        leads_totales.extend(leads_c100)
    except Exception as e:
        print(f"Error en Ciencuadras: {e}")

    print(f"\nScraping finalizado. Leads totales de dueños directos encontrados: {len(leads_totales)}")
    
    # 2. Subir a Google Sheets
    if leads_totales:
        try:
            append_leads_to_sheet(nombre_hoja, leads_totales)
        except FileNotFoundError:
            print("No se encontro el archivo credentials.json. Por favor agregalo en la raiz del proyecto para que se guarden los datos en Google Sheets.")
        except Exception as e:
            print(f"Error al guardar en Sheets: {e}")
    else:
        print("No se agregaron nuevos datos a Sheets hoy.")

if __name__ == "__main__":
    main()
