import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# --- CONFIGURATION ---
# L'URL du plan d'études (Change ça selon ta section !)
# Exemple ici: Master Data Science
BASE_URL = "https://edu.epfl.ch/studyplan/fr/bachelor/systemes-de-communication/"

def get_course_urls(url):
    print(f"🔍 Connexion à {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Vérifie s'il y a une erreur (404, etc)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    course_links = set() # 'set' permet d'éviter les doublons automatiquement

    # Recherche des liens. Sur l'EPFL, les liens intéressants contiennent souvent 'coursebook'
    # On cherche tous les <a> qui ont un href
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Filtre basique : on cherche les mots clés dans l'url
        if 'coursebook' in href and 'fr' in href: 
            # On recrée l'URL complète (absolue)
            full_url = urllib.parse.urljoin(url, href)
            course_links.add(full_url)

    return list(course_links)

# --- EXECUTION ---
if __name__ == "__main__":
    urls = get_course_urls(BASE_URL)
    
    print(f"\n✅ {len(urls)} cours trouvés !")
    
    # On sauvegarde dans un fichier texte pour ne pas les perdre
    with open("urls_cours.txt", "w", encoding="utf-8") as f:
        for link in urls:
            print(f" - {link}")
            f.write(link + "\n")
            
    print("\n💾 Les liens sont sauvegardés dans 'urls_cours.txt'")