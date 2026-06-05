from utils.sheets import get_sheets_client

try:
    client = get_sheets_client()
    sheet = client.open("CGBI Leads Finca Raiz").worksheet("Auditoría")
    sheet.clear()
    sheet.append_row(["Fecha", "Tipo", "Precio", "Ubicación", "Link", "Razón de Descarte"])
    print("Pestaña de Auditoría limpiada exitosamente.")
except Exception as e:
    print("No se pudo limpiar la auditoria", e)
