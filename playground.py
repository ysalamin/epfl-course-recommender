from bs4 import BeautifulSoup

# 1. Je simule le HTML que je vois sur ton image
html_simule = """
<button class="collapse-title">
    Informatique
    <br>
    <span class="d-block">2025-2026 Master semestre 2</span>
</button>
"""

soup = BeautifulSoup(html_simule, "html.parser")

# 2. Je reproduis ta logique
btn = soup.find("button")
span_tag = btn.find("span")

full_text = btn.get_text(strip=True)
span_text = span_tag.get_text(strip=True)

# 3. J'affiche la vérité
print(f"--- Full Text:   '{full_text}'")
print(f"--- Span Text:   '{span_text}'")

# 4. Je teste la soustraction
resultat = full_text.replace(span_text, "")
print(f"--- Résultat final: '{resultat}'")