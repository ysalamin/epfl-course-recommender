import os
import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer

# Config — resolved from this file's location (repo root = parent of core/) so the
# script works regardless of cwd, whether run as `python -m core.indexer` from the
# repo root or `python indexer.py` from core/.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(REPO_ROOT, "data", "cours_data_2026.json")
DB_PATH = os.path.join(REPO_ROOT, "epfl_cours_db")
COLLECTION_NAME = "cours_epfl"
BATCH_SIZE = 50

def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input courses file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f :
        data = json.load(f)
    print(f"{len(data)} courses loaded from {filepath}")
    return data

def setup_chromaDB(db_path, collection_name):
    client = chromadb.PersistentClient(path=db_path)

    # Avoid duplicate
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = client.create_collection(name=collection_name)
    return collection

def main():
    course_data = load_data(INPUT_FILE)
    if not course_data:
        sys.exit(f"No courses found in {INPUT_FILE} — aborting indexation.")

    print("model and db setup / loading...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    db = setup_chromaDB(DB_PATH, COLLECTION_NAME)


    total_length = len(course_data)

    for i in range(0, total_length, BATCH_SIZE):
        batch = course_data[i: BATCH_SIZE + i]

        # Required by ChromaDB :
        ids = []
        documents = []
        metadatas = []

        for cours in batch:
            url = cours.get("url")
            title = cours.get("title")
            content = cours.get("content")
            metadata = cours.get("metadata")

            if not url or not content: continue # Skipping broken course

            ids.append(url)
            documents.append(content)

            # For the metadata, we can't stock dict, we need Jstring
            meta_str = json.dumps(metadata)
            metadatas.append({"title": title, "url": url, "metadata": meta_str})

        if documents:
            embeddings = model.encode(documents).tolist()
            db.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
        print(f" {min(i+BATCH_SIZE, total_length)} / {total_length} courses processed")

    print("Indexation finished")




if __name__ == "__main__":
    main()
