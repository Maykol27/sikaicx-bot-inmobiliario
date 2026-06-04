from utils.sheets import get_sheets_client

client = get_sheets_client()
sheet = client.open("CGBI Leads Finca Raiz").sheet1

data = sheet.get_all_values()
rows_to_keep = []
for row in data:
    # Ignorar las filas que inserté con el link falso "/demo"
    if len(row) > 4 and "/demo" in str(row[4]):
        continue
    rows_to_keep.append(row)

sheet.clear()
sheet.update("A1", rows_to_keep)
print("Leads ficticios eliminados exitosamente.")
