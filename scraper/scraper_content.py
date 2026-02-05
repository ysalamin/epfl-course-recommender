import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os

# --- CONFIGURATION ---
INPUT_URLS_FILE = "../data/urls_cours.txt"
OUTPUT_JSON_FILE = "../data/cours_data_final.json"

def get_course_details(url):
    try:
        response = requests.get(url)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.content, "html.parser")

        # Retrieving the title of the course
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "No title"
        
        # Examples : Bachelor Syscom, Bachelor info, Master Data science...
        course_metadata = []
        plans_container = soup.find("div", class_="study-plans")

        if plans_container:
            accordeons = plans_container.find_all("button", class_="collapse-title")
            for accordeon in accordeons:
                span_tag = accordeon.find("span")
                if not span_tag: continue

                # Extraction Section (Syscom) and level(Master)
                full_accordeon_text = accordeon.get_text(strip=True)
                span_text = span_tag.getText(strip=True)
                section_name = full_accordeon_text.replace(span_text, "").strip()

                level = "Autre"
                if "Master" in span_text: level = "Master"
                elif "Bachelor" in span_text: level = "Bachelor"

                # Mandatory / Optional extraction
                is_mandatory = False
                accordeon_content_div = accordeon.find_next_sibling("div", class_="collapse-item")
                if accordeon_content_div:
                    # Look for "obligatoire" or "optionnel" in the list items
                    all_text = accordeon_content_div.get_text().lower()
                    if "obligatoire" in all_text or "mandatory" in all_text:
                        is_mandatory = True
                    elif "optionnel" in all_text or "optional" in all_text:
                        is_mandatory = False

                course_metadata.append({
                    "level": level,
                    "section": section_name,
                    "isMandatory": is_mandatory
                })


        # Fallback if empty
        if not course_metadata:
            course_metadata.append({"level": "unknown", "section": "unknown", "isMandatory": "unknown"})

        # Content to be vectorize (main content, document)
        content_div = soup.find("div", class_="course-details")
        if not content_div:
            content_div = soup.find("main") or soup.body

        relevant_text = ""
        if content_div:
            relevant_text = content_div.get_text(separator=" ", strip=True)

        return {
            "url": url,
            "title": title,
            "content": f"{title}. {relevant_text}",
            "metadata": course_metadata
        }



    except Exception as e:
        print(f"Error retrieving : {url}, {e}")
        return None

def main():
    print("Start scraping...")

    if not os.path.exists(INPUT_URLS_FILE):
        print("Input_urls_file not found, path problem")

    with open(INPUT_URLS_FILE, "r", encoding="utf-8") as f :
        urls = [line.strip() for line in f if line.strip()]

    courses_data = []

    for i, url in enumerate(urls):
        print(f"{i} / {len(urls)} / {url.split('/')[-1][:40]}...")
        content = get_course_details(url)
        if content:
            courses_data.append(content)
        
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(courses_data, f, ensure_ascii=False, indent=4)

    print("Done, you can now run python indexer.py")


if __name__ == "__main__":
    main()