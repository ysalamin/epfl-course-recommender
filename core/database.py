import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi
import json
import os

from core.utils import DB_PATH, COLLECTION_NAME


def initialize_database(embedder):
    """
    Initialize ChromaDB from scratch using cours_data_final.json.
    Runs on first launch when the database doesn't exist.
    """
    DATA_FILE = "./data/cours_data_final.json"
    BATCH_SIZE = 50

    if not os.path.exists(DATA_FILE):
        st.error(f"❌ Fichier de données introuvable: {DATA_FILE}")
        st.stop()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        course_data = json.load(f)

    st.info(f"📚 Chargement de {len(course_data)} cours depuis {DATA_FILE}")

    client = chromadb.PersistentClient(path=DB_PATH)

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    total_length = len(course_data)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(0, total_length, BATCH_SIZE):
        batch = course_data[i:i + BATCH_SIZE]

        ids, documents, metadatas = [], [], []

        for cours in batch:
            url = cours.get("url")
            title = cours.get("title")
            content = cours.get("content")
            metadata = cours.get("metadata")

            if not url or not content:
                continue

            ids.append(url)
            documents.append(content)
            metadatas.append({"title": title, "url": url, "metadata": json.dumps(metadata)})

        if documents:
            embeddings = embedder.encode(documents).tolist()
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

        processed = min(i + BATCH_SIZE, total_length)
        progress_bar.progress(processed / total_length)
        status_text.text(f"Indexation: {processed}/{total_length} cours traités...")

    progress_bar.empty()
    status_text.empty()
    st.success("✅ Base de données créée avec succès!")

    return collection


@st.cache_resource
def load_resources():
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

    if not os.path.exists(DB_PATH):
        st.warning("⚠️ Base de données introuvable. Premier lancement détecté.")
        st.info("🔄 Indexation des cours en cours... (cela peut prendre 1-2 minutes)")
        collection = initialize_database(embedder)
    else:
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)

    all_docs = collection.get()
    tokenized_corpus = [doc.split() for doc in all_docs['documents']]
    bm25 = BM25Okapi(tokenized_corpus)

    return embedder, collection, bm25, all_docs
