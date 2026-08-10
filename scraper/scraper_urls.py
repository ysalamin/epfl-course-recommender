import sys
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# La console Windows (cp1252) ne sait pas afficher les emojis -> on force l'UTF-8.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# --- CONFIGURATION ---
# Point de départ du crawl : on découvre automatiquement tous les plans d'études
# (bachelor, master, mineurs, etc.) à partir de la page d'accueil edu.epfl.ch.
START_URL = "https://edu.epfl.ch/"
DOMAIN = "edu.epfl.ch"
OUTPUT_FILE = "../data/urls_cours_2026.txt"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Délai (en secondes) entre deux requêtes pour rester poli avec le serveur EPFL.
REQUEST_DELAY = 0.5


def fetch(url):
    """Récupère et parse une page. Renvoie un objet BeautifulSoup ou None en cas d'erreur."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"   ⚠️  Erreur sur {url} : {e}", flush=True)
        return None


def discover_studyplans(start_url):
    """
    Crawler tous les plans d'études.

    On part de la page d'accueil, on collecte tous les liens /studyplan/fr/...
    puis on visite chacun d'eux (BFS) pour découvrir d'éventuels plans liés,
    en restant strictement sur le domaine edu.epfl.ch.
    """
    print(f"🌐 Découverte des plans d'études depuis {start_url}...", flush=True)

    to_visit = [start_url]
    visited = set()
    studyplans = set()

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        soup = fetch(url)
        time.sleep(REQUEST_DELAY)
        print(f"   ...visité {len(visited)} pages, {len(studyplans)} plans trouvés, "
              f"{len(to_visit)} en attente — {url}", flush=True)
        if soup is None:
            continue

        for link in soup.find_all('a', href=True):
            full_url = urllib.parse.urljoin(url, link['href'])
            parsed = urllib.parse.urlparse(full_url)

            if parsed.netloc != DOMAIN:
                continue

            # On normalise (on enlève query/fragment) pour dédupliquer proprement.
            clean_url = f"https://{DOMAIN}{parsed.path}"

            # Les pages de cours individuelles (.../coursebook/...) contiennent aussi
            # '/studyplan/fr/' dans leur chemin : il faut les exclure, sinon le BFS
            # explose en visitant chaque cours comme s'il s'agissait d'un plan d'études.
            if '/studyplan/fr/' in parsed.path and '/coursebook/' not in parsed.path:
                if clean_url not in studyplans:
                    studyplans.add(clean_url)
                    # On explore aussi ce plan pour trouver d'autres plans liés.
                    if clean_url not in visited:
                        to_visit.append(clean_url)

    print(f"📚 {len(studyplans)} pages de plan d'études trouvées.", flush=True)
    return sorted(studyplans)


def collect_course_urls(studyplan_url):
    """Extrait tous les liens coursebook (fr) d'une page de plan d'études."""
    soup = fetch(studyplan_url)
    time.sleep(REQUEST_DELAY)
    if soup is None:
        return set()

    course_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'coursebook' in href and 'fr' in href:
            full_url = urllib.parse.urljoin(studyplan_url, href)
            # Normalisation (retrait query/fragment) pour dédupliquer.
            parsed = urllib.parse.urlparse(full_url)
            course_links.add(f"https://{parsed.netloc}{parsed.path}")

    return course_links


# --- EXECUTION ---
if __name__ == "__main__":
    studyplans = discover_studyplans(START_URL)

    all_courses = set()
    for i, plan in enumerate(studyplans, 1):
        before = len(all_courses)
        all_courses |= collect_course_urls(plan)
        found = len(all_courses) - before
        print(f"[{i}/{len(studyplans)}] +{found:>3} cours ({len(all_courses)} au total) — {plan}", flush=True)

    urls = sorted(all_courses)
    print(f"\n✅ {len(urls)} URLs de cours uniques trouvées !", flush=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for link in urls:
            f.write(link + "\n")

    print(f"💾 Sauvegardé dans '{OUTPUT_FILE}'", flush=True)
