import json
import chromadb
from sentence_transformers import SentenceTransformer
import os

# --- CONFIGURATION ---
# On pointe vers le fichier final (assure-toi d'avoir lancé le scraper complet avec ce nom)
INPUT_FILE = "cours_data_final.json"
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"

def main():
    print(f"📂 Lecture du fichier : {INPUT_FILE} ...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : Le fichier {INPUT_FILE} est introuvable.")
        print("💡 As-tu lancé le scraper complet ?")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        cours_data = json.load(f)

    print(f"   -> {len(cours_data)} cours bruts trouvés.")

    # --- ÉTAPE 1 : DÉDOUBLONNAGE ---
    # On garde la logique pour éviter d'avoir 2x le même cours
    unique_courses = {}
    
    for cours in cours_data:
        titre = cours['titre'].strip()
        
        # On ignore les cours vides
        if not titre or titre == "Sans titre":
            continue
            
        # Si on ne l'a pas encore, on l'ajoute
        if titre not in unique_courses:
            # PLUS DE NETTOYAGE ICI : On fait confiance au scraper !
            unique_courses[titre] = cours
    
    clean_data = list(unique_courses.values())
    print(f"✨ Nettoyage terminé : On passe de {len(cours_data)} à {len(clean_data)} cours uniques.")

    # --- ÉTAPE 2 : PRÉPARATION DU CERVEAU (CHROMA) ---
    print("🧠 Chargement du modèle IA (SentenceTransformer)...")
    # On garde ce modèle, c'est le meilleur compromis vitesse/qualité
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    chroma_client = chromadb.PersistentClient(path=DB_PATH)
    
    # Reset de la base pour repartir à zéro
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print("🗑️ Ancienne base supprimée.")
    except:
        pass 

    collection = chroma_client.create_collection(name=COLLECTION_NAME)

    # --- ÉTAPE 3 : INDEXATION PAR LOTS (BATCHING) ---
    batch_size = 200
    total = len(clean_data)
    
    print("⚙️ Création des vecteurs et enregistrement dans la base...")
    
    for i in range(0, total, batch_size):
        batch = clean_data[i : i + batch_size]
        
        ids = [c["url"] for c in batch]
        documents = [c["full_embedding_text"] for c in batch]
        
        # On prépare les métadonnées
        # (C'est ici qu'on pourra ajouter le tag 'SHS' plus tard pour le filtre avancé)
        metadatas = []
        for c in batch:
            # On récupère la liste 'plans', ou une liste vide si elle n'existe pas
            plans_data = c.get("plans", [])
            
            # On transforme cette liste en TEXTE (string) pour que ChromaDB l'accepte
            plans_str = json.dumps(plans_data) 
            
            metadatas.append({
                "titre": c["titre"], 
                "url": c["url"],
                "plans_json": plans_str # On stocke la string JSON ici
            })
        # Vectorisation
        embeddings = model.encode(documents).tolist()
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"   [{min(i + batch_size, total)}/{total}] cours indexés...")

    print("🎉 SUCCÈS ! Base de données générée avec succès.")
    print("👉 Tu peux maintenant lancer 'streamlit run app.py'")

if __name__ == "__main__":
    main()