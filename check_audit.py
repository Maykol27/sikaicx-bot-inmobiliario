from utils.sheets import get_sheets_client

def check():
    client = get_sheets_client()
    sheet = client.open("CGBI Leads Finca Raiz").worksheet("Auditoría")
    data = sheet.get_all_values()
    print(f"Total rows in Auditoria: {len(data)}")
    if len(data) > 1:
        print(f"First data row date: {data[1][0]}")
        print(f"Last data row date: {data[-1][0]}")

check()
