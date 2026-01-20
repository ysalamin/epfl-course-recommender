# test_scraper.py
import json
# On importe ta fonction depuis ton fichier principal
from scraper_content import get_course_details 

# L'URL exacte de ton screenshot (Software Construction)
# Remplace-la si tu veux tester un autre cours
TEST_URL = "https://edu.epfl.ch/coursebook/en/software-construction-CS-214"

def run_test():
    print(f"🔬 Test en cours sur : {TEST_URL}")
    
    data = get_course_details(TEST_URL)
    
    if data:
        print("\n✅ SUCCÈS ! Voici ce qu'on a trouvé pour les plans :")
        # On affiche joliment juste la partie qui nous intéresse
        print(json.dumps(data['plans'], indent=4, ensure_ascii=False))
        
        print("\n--- Header complet trouvé ---")
        # Vérifie que tu vois bien "Informatique" ici
        for p in data['plans']:
            print(f"Section: {p['full_header']} | Niveau: {p['niveau']} | Type: {p['type']}")
    else:
        print("❌ Échec : La fonction a renvoyé None.")

if __name__ == "__main__":
    run_test()