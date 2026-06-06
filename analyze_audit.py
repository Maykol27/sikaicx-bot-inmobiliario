from utils.sheets import get_sheets_client

def analyze():
    client = get_sheets_client()
    sheet = client.open("CGBI Leads Finca Raiz").worksheet("Auditoría")
    data = sheet.get_all_values()
    
    fechas = {}
    for row in data[1:]:
        f = row[0]
        fechas[f] = fechas.get(f, 0) + 1
        
    print(f"Desglose por fecha: {fechas}")

analyze()
