from utils.sheets import get_sheets_client
import collections

def analyze():
    client = get_sheets_client()
    sheet = client.open("CGBI Leads Finca Raiz").worksheet("Auditoría")
    data = sheet.get_all_values()
    
    yesterday_leads = [row for row in data if row[0] == '2026-06-05']
    
    reasons_count = collections.Counter([r[5] for r in yesterday_leads])
    print("--- RESUMEN DE RAZONES ---")
    for reason, count in reasons_count.most_common(15):
        print(f"{count} inmuebles -> {reason}")
        
    sospechosos = [r for r in yesterday_leads if "Descartado por defecto" in r[5]]
    print(f"\n--- POSIBLES FALSOS POSITIVOS ({len(sospechosos)}) ---")
    for s in sospechosos[:10]:
        print(s[4])

analyze()
