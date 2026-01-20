import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import os
import math
import json

# --- CONFIGURATION ---
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"

st.set_page_config(page_title="EPFL Course Recommender", page_icon="🎓", layout="wide")

# --- TA NOUVELLE LISTE COMPLETE ---
# Note: J'ai ajouté quelques alias anglais courants (Computer Science, Communication Systems) 
# pour t'assurer des résultats même si le scraper tombe sur la page EN.
PROGRAMMES = {
    "🌐 Tout explorer": (None, None),

    # BACHELORS
    "🏛️ Bachelor Architecture": (["Architecture"], "Bachelor"),
    "🧪 Bachelor Chimie": (["Chimie"], "Bachelor"),
    "⚗️ Bachelor Chimie et génie chimique": (["Chimie et génie chimique"], "Bachelor"),
    "🏭 Bachelor Génie chimique": (["Génie chimique"], "Bachelor"),
    "🏗️ Bachelor Génie civil": (["Génie civil", "Civil Engineering"], "Bachelor"),
    "⚙️ Bachelor Génie mécanique": (["Génie mécanique", "Mechanical Engineering"], "Bachelor"),
    "⚡ Bachelor Génie électrique": (["Génie électrique", "Electrical and Electronics"], "Bachelor"),
    "💻 Bachelor Informatique": (["Informatique", "Computer Science"], "Bachelor"),
    "🧬 Bachelor Sciences du vivant": (["Ingénierie des sciences du vivant", "Life Sciences"], "Bachelor"),
    "🧮 Bachelor Mathématiques": (["Mathématiques", "Mathematics"], "Bachelor"),
    "🔬 Bachelor Microtechnique": (["Microtechnique", "Microengineering"], "Bachelor"),
    "⚛️ Bachelor Physique": (["Physique", "Physics"], "Bachelor"),
    "🧱 Bachelor Matériaux": (["Science et génie des matériaux"], "Bachelor"),
    "🌍 Bachelor Environnement": (["Science et ingénierie de l'environnement"], "Bachelor"),
    "📡 Bachelor SysCom": (["Systèmes de communication", "Communication Systems"], "Bachelor"),

    # MASTERS (J'ai gardé ta structure exacte)
    "🏛️ Master Architecture": (["Architecture"], "Master"),
    "🧪 Master Chimie moléculaire": (["Chimie moléculaire et biologique"], "Master"),
    "📊 Master Data Science": (["Data Science"], "Master"),
    "🏗️ Master Génie civil": (["Génie civil", "Civil Engineering"], "Master"),
    "⚙️ Master Génie mécanique": (["Génie mécanique", "Mechanical Engineering"], "Master"),
    "☢️ Master Génie nucléaire": (["Génie nucléaire", "Nuclear Engineering"], "Master"),
    "⚡ Master Génie électrique": (["Génie électrique", "Electrical and Electronics"], "Master"),
    "📜 Master Humanités digitales": (["Humanités digitales", "Digital Humanities"], "Master"),
    "💻 Master Informatique": (["Informatique", "Computer Science"], "Master"),
    "🛡️ Master Cybersec": (["Informatique - Cybersecurity", "Cyber security"], "Master"),
    "🧬 Master Sciences du vivant": (["Ingénierie des sciences du vivant", "Life Sciences"], "Master"),
    "💰 Master Ingénierie financière": (["Ingénierie financière", "Financial Engineering"], "Master"),
    "🧮 Master Ingénierie mathématique": (["Ingénierie mathématique"], "Master"),
    "⚛️ Master Ingénierie physique": (["Ingénierie physique"], "Master"),
    "🌱 Master Management durable": (["Management durable et technologie"], "Master"),
    "🚀 Master Management & Tech": (["Management, technologie et entrepreneuriat"], "Master"),
    "📐 Master Mathématiques": (["Mathématiques"], "Master"),
    "🔬 Master Micro-Nanotech": (["Micro- and Nanotechnologies"], "Master"),
    "🔬 Master Microtechnique": (["Microtechnique", "Microengineering"], "Master"),
    "🧠 Master Neuro-X": (["Neuro-X"], "Master"),
    "⚛️ Master Physique": (["Physique"], "Master"),
    "🤖 Master Robotique": (["Robotique", "Robotics"], "Master"),
    "🧱 Master Matériaux": (["Science et génie des matériaux"], "Master"),
    "💻 Master Computational Science": (["Science et ingénierie computationnelles"], "Master"),
    "🌌 Master Quantique": (["Science et ingénierie quantiques"], "Master"),
    "🔋 Master Energie": (["Science et technologie de l'énergie", "Energy"], "Master"),
    "🌍 Master Environnement": (["Sciences et ingénierie de l'environnement"], "Master"),
    "📈 Master Statistique": (["Statistique"], "Master"),
    "📡 Master SysCom": (["Systèmes de communication", "Communication Systems"], "Master"),
    "🏙️ Master Systèmes urbains": (["Systèmes urbains"], "Master"),
}

# --- CHARGEMENT ---
def sigmoid(x): return 1 / (1 + math.exp(-(x + 6)))

@st.cache_resource
def load_models():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'), CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

@st.cache_resource
def load_db_collection():
    return chromadb.PersistentClient(path=DB_PATH).get_collection(name=COLLECTION_NAME)

@st.cache_resource
def init_bm25(documents):
    return BM25Okapi([doc.split(" ") for doc in documents])

try:
    with st.spinner("Chargement..."):
        sentence_transformer, model_reranker = load_models()
        collection = load_db_collection()
        all_docs = collection.get()
        documents_list = all_docs['documents']
        ids_list = all_docs['ids']
        metadatas_list = all_docs['metadatas']
        bm25_engine = init_bm25(documents_list)
except Exception as e:
    st.error(f"Erreur DB : {e}")
    st.stop()

# --- INTERFACE ---
with st.sidebar:
    st.header("👤 Votre Profil")
    
    # 1. Le sélecteur de programme
    selected_program_name = st.selectbox("Programme", options=list(PROGRAMMES.keys()), index=0) # index 0 pour "Tout explorer" par défaut
    target_aliases, target_level = PROGRAMMES[selected_program_name]
    
    st.markdown("---")
    st.header("⚙️ Paramètres de recherche")
    top_k = st.slider("Nombre de résultats max", min_value=5, max_value=100, value=10, step=5)    # 2. Section Debug améliorée


st.title("🎓 EPFL Course Recommender")
job_offer = st.text_area("📋 Ce que vous cherchez...", height=100)
search_btn = st.button("🚀 Trouver les cours", type="primary", use_container_width=True)

# --- LOGIQUE ---
if search_btn and job_offer:
    with st.spinner("Recherche..."):
        # 1. Retrieval
        query_vector = sentence_transformer.encode(job_offer).tolist()
        
        # ON UTILISE top_k * 2 pour avoir de la marge pour le filtrage
        limit_search = top_k * 2 
        
        v_results = collection.query(query_embeddings=[query_vector], n_results=limit_search)
        v_ids = v_results['ids'][0] if v_results['ids'] else []
        
        bm25_top = bm25_engine.get_top_n(job_offer.split(" "), documents_list, n=limit_search)
        bm25_ids = [ids_list[documents_list.index(d)] for d in bm25_top if d in documents_list]
        
        all_ids = list(set(v_ids + bm25_ids))
        candidates, final_ids, final_metas = [], [], []

        # 2. Filtering
        for doc_id in all_ids:
            try:
                idx = ids_list.index(doc_id)
                meta = metadatas_list[idx]
                plans = json.loads(meta.get('plans_json', '[]'))
                
                keep = False
                badge = ""
                
                if target_aliases is None: # Tout explorer
                    keep = True
                else:
                    # Vérification LISTE alias
                    for plan in plans:
                        p_head = plan.get('full_header', '').lower()
                        p_lvl = plan.get('niveau', '').lower()
                        
                        # On vérifie si UN des alias (ex: "informatique" OU "computer science") est dans le header
                        match_section = any(alias.lower() in p_head for alias in target_aliases)
                        match_level = target_level.lower() in p_lvl
                        
                        if match_section and match_level:
                            keep = True
                            badge = plan.get('type', 'Inconnu')
                            break
                
                if keep:
                    if "Summer workshop" in meta['titre']: continue
                    candidates.append([job_offer, documents_list[idx]])
                    final_ids.append(doc_id)
                    meta['badge'] = badge
                    final_metas.append(meta)
            except: continue

        # 3. Reranking & Display
        if candidates:
            scores = model_reranker.predict(candidates)
            ranked = sorted(zip(scores, final_ids, final_metas, candidates), key=lambda x: x[0], reverse=True)
            
            st.success(f"{len(ranked)} cours trouvés")
            for i in range(min(top_k, len(ranked))):
                score, did, meta, content = ranked[i]
                badge_txt = meta.get('badge', '')
                color = "red" if "bligatoire" in badge_txt or "andatory" in badge_txt else "green"
                
                st.markdown(f"### [{meta['titre']}]({did})")
                if badge_txt: st.caption(f":{color}[{badge_txt}]")
                st.progress(sigmoid(score), text=f"Pertinence: {sigmoid(score):.0%}")
                with st.expander("Détails"):
                    st.write(content[1][:400]+"...")
                st.divider()
        else:
            st.warning("Aucun cours trouvé.")
