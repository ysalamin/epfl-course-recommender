import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os

# --- CONFIGURATION ---
INPUT_URLS_FILE = "urls_cours.txt"
OUTPUT_JSON_FILE = "cours_data_final.json"

def get_course_details(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. TITRE
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "Sans titre"
        
        # 2. PLANS D'ÉTUDES (Méthode CSS précise)
        study_plans = []
        plans_container = soup.find('div', class_='study-plans')
        
        if plans_container:
            buttons = plans_container.find_all('button', class_='collapse-title')
            for btn in buttons:
                span_tag = btn.find('span')
                if not span_tag: continue
                
                # Extraction Section et Niveau
                full_btn_text = btn.get_text(strip=True)
                span_text = span_tag.get_text(strip=True)
                section_name = full_btn_text.replace(span_text, "").strip()
                
                level = "Autre"
                if "Bachelor" in span_text: level = "Bachelor"
                elif "Master" in span_text: level = "Master"
                
                # Extraction Type (avec Regex)
                content_div = btn.find_next_sibling('div', class_='collapse-item')
                course_type = "Inconnu"
                
                if content_div:
                    block_text = content_div.get_text(separator="\n")
                    # Regex pour capturer "Type: obligatoire" ou "Type: mandatory"
                    match = re.search(r"(?i)Type\s*:\s*(.*)", block_text)
                    if match:
                        course_type = match.group(1).strip().lower()
                
                study_plans.append({
                    "full_header": section_name,
                    "niveau": level,
                    "type": course_type
                })

        # Fallback si vide
        if not study_plans:
            study_plans.append({"full_header": "Général", "niveau": "Inconnu", "type": "Inconnu"})

        # 3. CONTENU IA
        main_content = soup.find('div', class_='main-content') or soup.find('main') or soup.body
        relevant_text = ""
        if main_content:
            for junk in main_content.find_all(['nav', 'header', 'footer', 'form', 'script', 'style', 'div.study-plans']):
                junk.decompose()
            full_text = main_content.get_text(separator=" ", strip=True)
            match_start = re.search(r"(Résumé|Summary|Contenu|Content)\s*[:\.]?", full_text, re.IGNORECASE)
            start_index = match_start.start() if match_start else 0
            relevant_text = full_text[start_index:2000]

        return {
            "url": url,
            "titre": title,
            "full_embedding_text": f"{title}. {relevant_text}",
            "plans": study_plans
        }

    except Exception as e:
        print(f"❌ Erreur {url}: {e}")
        return None

def main():
    print("🚀 Démarrage du SCRAPER FINAL...")
    
    if not os.path.exists(INPUT_URLS_FILE):
        print(f"❌ Fichier {INPUT_URLS_FILE} introuvable !")
        return

    with open(INPUT_URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"🎯 {len(urls)} cours à analyser.")
    cours_data = []
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url.split('/')[-1][:40]}...")
        details = get_course_details(url)
        if details:
            cours_data.append(details)
        
        if (i+1) % 50 == 0:
            with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(cours_data, f, ensure_ascii=False, indent=4)
        
        time.sleep(0.1) 

    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(cours_data, f, ensure_ascii=False, indent=4)
    print("✅ TERMINE ! Lance maintenant 'python indexer.py'")

if __name__ == "__main__":
    main()