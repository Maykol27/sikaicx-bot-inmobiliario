from bs4 import BeautifulSoup

def analyze(file_path):
    print(f"\n--- Analyzing {file_path} ---")
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    links = soup.find_all("a", href=True)
    prop_links = []
    for l in links:
        href = l['href']
        if '/inmueble/' in href or '-venta-' in href or '-arriendo-' in href or 'inmuebles/' in href:
            prop_links.append(l)
    
    print(f"Found {len(prop_links)} property links")
    
    if prop_links:
        # Get the parent of the first link, to see the card structure
        first_card = prop_links[0].find_parent("div", class_=True)
        if first_card:
            print("First card classes:", first_card.get('class'))
            # Try to print some text
            print("Text snippet:", first_card.text[:200].replace('\n', ' '))
            
        print("Sample links:")
        for l in prop_links[:5]:
            print(l['href'])

analyze("metrocuadrado_debug.html")
analyze("ciencuadras_debug.html")
