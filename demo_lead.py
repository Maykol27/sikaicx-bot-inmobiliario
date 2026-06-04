from utils.sheets import append_leads_to_sheet
from datetime import datetime

demo_leads = [
    {
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Tipo": "Venta",
        "Precio": "$850.000.000",
        "Ubicación": "Bogotá - Cedritos",
        "Link": "https://www.fincaraiz.com.co/apartamento-en-venta-cedritos/demo",
        "Teléfono": "300 123 4567",
        "Descripción": "Dueño directo vende hermoso apartamento esquinero, muy iluminado. Trato directo sin comisionistas. Motivo viaje.",
        "Estado": "Pendiente de Llamar"
    },
    {
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Tipo": "Arriendo",
        "Precio": "$3.500.000",
        "Ubicación": "Bogotá - Chicó Navarra",
        "Link": "https://www.metrocuadrado.com/apartamento-en-arriendo-chico/demo",
        "Teléfono": "315 987 6543",
        "Descripción": "Arriendo apartamento directamente. Cero intermediarios, se exige póliza de seguro SURA. Excelente estado.",
        "Estado": "Pendiente de Llamar"
    }
]

try:
    print("Inyectando leads de demostración...")
    append_leads_to_sheet("CGBI Leads Finca Raiz", demo_leads)
    print("¡Leads inyectados con éxito!")
except Exception as e:
    print(f"Error: {e}")
