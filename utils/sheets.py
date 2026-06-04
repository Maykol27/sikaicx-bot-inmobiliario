import gspread
from google.oauth2.service_account import Credentials
import os

# Scopes requeridos por Google API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheets_client(credentials_path="credentials.json"):
    """
    Inicializa y retorna el cliente de gspread usando el archivo JSON de credenciales.
    """
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"No se encontro el archivo de credenciales en {credentials_path}")
        
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_existing_links(spreadsheet_name):
    """
    Obtiene todos los links que ya están guardados en la hoja para evitar duplicados.
    """
    try:
        client = get_sheets_client()
        sheet = client.open(spreadsheet_name).sheet1
        existing_data = sheet.get_all_values()
        
        # Si la hoja está vacía
        if not existing_data or len(existing_data) <= 1:
            return set()
            
        # Asumiendo que "Link" está en la columna 4 (índice 4, 0-indexed)
        # La estructura es: ["Fecha", "Tipo", "Precio", "Ubicación", "Link", "Teléfono", "Descripción", "Estado"]
        links = set()
        for row in existing_data[1:]: # Ignorar la fila de encabezados
            if len(row) > 4:
                links.add(row[4].strip())
        return links
    except Exception as e:
        print(f"Error obteniendo links existentes (posiblemente la hoja es nueva): {e}")
        return set()

def append_leads_to_sheet(spreadsheet_name, leads):
    """
    Agrega una lista de leads (diccionarios) a la hoja de Google Sheets.
    Crea los encabezados si la hoja está vacía.
    """
    if not leads:
        print("No hay leads nuevos para agregar.")
        return

    client = get_sheets_client()
    try:
        sheet = client.open(spreadsheet_name).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        raise Exception(f"No se pudo abrir la hoja '{spreadsheet_name}'. Asegurate de haberla compartido con el correo del bot.")

    existing_data = sheet.get_all_values()
    headers = ["Fecha", "Tipo", "Precio", "Ubicación", "Link", "Teléfono", "Descripción", "Estado"]
    
    if not existing_data:
        sheet.append_row(headers)

    rows_to_insert = []
    for lead in leads:
        row = [
            lead.get("Fecha", ""),
            lead.get("Tipo", ""),
            lead.get("Precio", ""),
            lead.get("Ubicación", ""),
            lead.get("Link", ""),
            lead.get("Teléfono", ""),
            lead.get("Descripción", ""),
            lead.get("Estado", "")
        ]
        rows_to_insert.append(row)
        
    if rows_to_insert:
        sheet.append_rows(rows_to_insert)
        print(f"Se agregaron {len(rows_to_insert)} nuevos leads a {spreadsheet_name}")
