from utils.sheets import get_sheets_client

def get_today():
    client = get_sheets_client()
    sheet = client.open("CGBI Leads Finca Raiz").worksheet("Auditoría")
    data = sheet.get_all_values()
    
    today_leads = [row for row in data if row[0] == '2026-06-06']
    
    import json
    # Solo necesitamos Link y Razón
    results = [{"Link": r[4], "Reason": r[5]} for r in today_leads]
    
    with open('today_discarded.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

get_today()
