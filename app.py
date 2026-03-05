# CRITICAL: Patch SQLite for ChromaDB on Streamlit Cloud (Linux)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # Windows/local environment - use standard sqlite3
    pass

import streamlit as st
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from rank_bm25 import BM25Okapi
import math
import json
import re
import os
import numpy as np
from job_examples import JOB_EXAMPLES

# Must be first Streamlit command
st.set_page_config(
    page_title="EPFL Course Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CONST
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"
TOP_K_RETRIEVAL = 20  # How many candidates each retrieval pass (BM25 + semantic) returns

# Allowlist for sections (separate Bachelor and Master lists)
BACHELOR_SECTIONS = [
    'Architecture', 'Chimie', 'Chimie et génie chimique', 'Génie chimique',
    'Génie civil', 'Génie mécanique', 'Génie électrique et électronique',
    'Informatique', 'Ingénierie des sciences du vivant', 'Mathématiques',
    'Microtechnique', 'Physique', 'Science et génie des matériaux',
    'Sciences et ingénierie de l\'environnement', 'Systèmes de communication'
]

MASTER_SECTIONS = [
    'Architecture', 'Chimie moléculaire et biologique', 'Data Science',
    'Génie chimique et biotechnologie', 'Génie civil', 'Génie mécanique',
    'Génie nucléaire', 'Génie électrique et électronique', 'Humanités digitales',
    'Informatique', 'Informatique - Cybersecurity', 'Ingénierie des sciences du vivant',
    'Ingénierie financière', 'Ingénierie mathématique', 'Ingénierie physique',
    'Management durable et technologie', 'Management, technologie et entrepreneuriat',
    'Mathématiques - master', 'Micro- and Nanotechnologies for Integrated Systems',
    'Microtechnique', 'Neuro-X', 'Physique - master', 'Robotique',
    'Science et génie des matériaux', 'Science et ingénierie computationnelles',
    'Science et ingénierie quantiques', 'Science et technologie de l\'énergie',
    'Sciences et ingénierie de l\'environnement', 'Statistique', 'Systèmes urbains'
]

# Combined list of (display_name, section_name, level), sorted alphabetically
ALL_SECTIONS = sorted(
    [(f"{s} (Bachelor)", s, "Bachelor") for s in BACHELOR_SECTIONS] +
    [(f"{s} (Master)", s, "Master") for s in MASTER_SECTIONS],
    key=lambda x: x[0]
)


def initialize_database(embedder):
    """
    Initialize ChromaDB from scratch using cours_data_final.json
    This runs on first launch when the database doesn't exist
    """
    DATA_FILE = "./data/cours_data_final.json"
    BATCH_SIZE = 50

    # Load course data
    if not os.path.exists(DATA_FILE):
        st.error(f"❌ Fichier de données introuvable: {DATA_FILE}")
        st.stop()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        course_data = json.load(f)

    st.info(f"📚 Chargement de {len(course_data)} cours depuis {DATA_FILE}")

    # Setup ChromaDB
    client = chromadb.PersistentClient(path=DB_PATH)

    # Delete collection if exists (cleanup)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    # Process in batches
    total_length = len(course_data)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(0, total_length, BATCH_SIZE):
        batch = course_data[i:i + BATCH_SIZE]

        ids = []
        documents = []
        metadatas = []

        for cours in batch:
            url = cours.get("url")
            title = cours.get("title")
            content = cours.get("content")
            metadata = cours.get("metadata")

            if not url or not content:
                continue

            ids.append(url)
            documents.append(content)

            # Metadata as JSON string (ChromaDB limitation)
            meta_str = json.dumps(metadata)
            metadatas.append({"title": title, "url": url, "metadata": meta_str})

        if documents:
            embeddings = embedder.encode(documents).tolist()
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

        # Update progress
        processed = min(i + BATCH_SIZE, total_length)
        progress = processed / total_length
        progress_bar.progress(progress)
        status_text.text(f"Indexation: {processed}/{total_length} cours traités...")

    progress_bar.empty()
    status_text.empty()
    st.success("✅ Base de données créée avec succès!")

    return collection


@st.cache_resource
def load_resources():

    # Models
    embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    # Check if DB exists, if not initialize it
    if not os.path.exists(DB_PATH):
        st.warning("⚠️ Base de données introuvable. Premier lancement détecté.")
        st.info("🔄 Indexation des cours en cours... (cela peut prendre 1-2 minutes)")
        collection = initialize_database(embedder)
    else:
        # DB exists, load normally
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)

    all_docs = collection.get()

    tokenized_corpus = [doc.split() for doc in all_docs['documents']]
    bm25 = BM25Okapi(tokenized_corpus)

    return embedder, reranker, collection, bm25, all_docs



def parse_course_metadata(content):
    """Extract course code, credits, and professor from content"""
    metadata = {
        "code": "N/A",
        "credits": "N/A",
        "professor": "Non spécifié",
        "language": "Non spécifié"
    }

    # Extract course code (e.g., "MATH-518", "ME-202")
    code_match = re.search(r'\b([A-Z]+-\d+)\b', content)
    if code_match:
        metadata["code"] = code_match.group(1)

    # Extract credits (e.g., "5 crédits")
    credits_match = re.search(r'(\d+)\s+crédits?', content, re.IGNORECASE)
    if credits_match:
        metadata["credits"] = credits_match.group(1)

    # Extract professor name - stop at next keyword to avoid capturing full description
    # Match "Enseignant:" followed by text until we hit "Langue", "Résumé", "Summary", "Content", etc.
    prof_match = re.search(r'Enseignant[:\s]+(.+?)(?=\s+(?:Langue|Résumé|Summary|Content|Contenu|Lire|Keywords|Mots-clés)[:.\s])', content, re.IGNORECASE)
    if prof_match:
        professor = prof_match.group(1).strip()
        # Additional safety check: if still too long, truncate
        if len(professor) > 60:
            metadata["professor"] = "Non spécifié"
        else:
            metadata["professor"] = professor

    # Extract language - stop at next keyword
    lang_match = re.search(r'Langue[:\s]+(.+?)(?=\s+(?:Résumé|Summary|Content|Contenu|Enseignant|Lire|Keywords|Mots-clés)[:.\s])', content, re.IGNORECASE)
    if lang_match:
        language = lang_match.group(1).strip()
        # Additional safety check: language should be short (Français, Anglais, etc.)
        if len(language) > 30:
            metadata["language"] = "Non spécifié"
        else:
            metadata["language"] = language

    return metadata


def calculate_score_percentage(score):
    """
    Convert reranker score to user-friendly percentage using sigmoid

    ADJUSTED FOR REAL-WORLD RERANKER SCORES:
    In practice, reranker scores are often very negative (-12 to -6 range)
    even for decent matches, especially with multilingual content.

    New mapping (pivot at -10):
    - Very poor (< -12): 15-35%
    - Poor (-12 to -10): 35-55%
    - Average (-10 to -8): 55-75%
    - Good (-8 to -6): 75-90%
    - Excellent (> -6): 90-99%

    Formula: sigmoid(0.5 * (score + 10))
    Pivot at score=-10 (scores above -10 get >50%, below get <50%)
    """
    # Handle edge cases
    if score is None:
        return 0.5  # Default to 50%

    # Very gentle sigmoid optimized for negative score ranges
    # k=0.5 for gentle slope, pivot at -10 for realistic reranker scores
    try:
        result = 1 / (1 + math.exp(-0.5 * (score + 10)))
        return max(0.15, min(0.99, result))  # Clamp between 15% and 99%
    except (OverflowError, ValueError):
        # Handle extreme values
        if score > 0:
            return 0.99
        else:
            return 0.15


def search_courses(query, filters, embedder, reranker, collection, bm25, all_data):
    """
    Hybrid retrieval pipeline:
    1. Metadata filtering  — narrow down to courses matching level/section/semester/type
    2. If query provided:
       a. BM25 retrieval   — keyword scoring on filtered subset, take top-K
       b. Semantic retrieval — cosine similarity on embeddings, take top-K
       c. Merge            — union of both top-K sets
       d. Rerank           — CrossEncoder on merged set, sort by score
    3. If no query: return all filtered courses alphabetically
    """
    target_level, target_section, semester_filter, course_type_filter = filters

    print(f"\n{'='*80}")
    print(f"FILTRES: level={target_level}, section={target_section}, semester={semester_filter}, type={course_type_filter}")
    print(f"Mode: Affichage de TOUS les cours correspondants aux filtres")
    print(f"{'='*80}\n")

    # Step 1: Get ALL courses matching strict filters (no query-based filtering yet)
    filtered_candidates = []

    for idx, cid in enumerate(all_data['ids']):
        meta = all_data['metadatas'][idx]
        plans = json.loads(meta.get('metadata', '[]'))

        # Check if ANY plan matches our criteria
        for plan in plans:
            lvl = plan.get('level', '')
            sec = plan.get('section', '').strip()
            course_type = plan.get('type', '')
            sem = plan.get('semester', '')

            # Strict filtering
            level_match = (lvl == target_level)
            section_match = (sec == target_section)
            if course_type_filter == "Tous":
                type_match = True
            else:
                type_match = (course_type == course_type_filter)

            # Semester match — strict for both Bachelor and Master
            semester_match = (sem == semester_filter)

            if level_match and section_match and type_match and semester_match:
                print(f"✓ MATCH: {meta.get('title', 'N/A')[:50]} | {lvl} | {sec} | {course_type} | {sem}")
                filtered_candidates.append({
                    "id": cid,
                    "content": all_data['documents'][idx],
                    "meta": meta,
                    "level": lvl,
                    "section": sec,
                    "type": course_type,
                    "semester": sem
                })
                break  # Course matched, no need to check other plans

    # Remove duplicates by title
    unique_titles = set()
    unique_candidates = []
    for candidate in filtered_candidates:
        title = candidate['meta']['title']
        if title not in unique_titles:
            unique_candidates.append(candidate)
            unique_titles.add(title)
    filtered_candidates = unique_candidates

    print(f"\nCours trouvés après filtrage (TOTAL): {len(filtered_candidates)}\n")

    if not filtered_candidates:
        return []

    # Step 2: No query — return everything alphabetically
    if not query or not query.strip():
        filtered_candidates.sort(key=lambda x: x['meta']['title'])
        for candidate in filtered_candidates:
            candidate['score'] = 0
        return filtered_candidates

    # Step 3: Hybrid retrieval — BM25 + Semantic on filtered subset only

    # Build a lookup: course id → position in all_data (needed for global BM25 scores)
    id_to_global_idx = {cid: idx for idx, cid in enumerate(all_data['ids'])}

    # --- BM25 retrieval ---
    query_tokens = query.split()
    all_bm25_scores = bm25.get_scores(query_tokens)  # scores for every doc in corpus

    bm25_scored = []
    for candidate in filtered_candidates:
        global_idx = id_to_global_idx.get(candidate['id'])
        score = float(all_bm25_scores[global_idx]) if global_idx is not None else 0.0
        bm25_scored.append((candidate, score))

    bm25_scored.sort(key=lambda x: x[1], reverse=True)
    bm25_top = bm25_scored[:TOP_K_RETRIEVAL]
    bm25_top_ids = {c['id'] for c, _ in bm25_top}

    print(f"📘 BM25 Top-{TOP_K_RETRIEVAL} (sur {len(filtered_candidates)} candidats filtrés):")
    for candidate, score in bm25_top:
        print(f"   BM25 {candidate['meta']['title'][:40]:40s} | Score: {score:.4f}")

    # --- Semantic retrieval ---
    query_embedding = embedder.encode(query)
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)

    # Fetch stored embeddings from ChromaDB for filtered candidates only
    filtered_ids = [c['id'] for c in filtered_candidates]
    chroma_result = collection.get(ids=filtered_ids, include=["embeddings"])
    id_to_embedding = {cid: emb for cid, emb in zip(chroma_result['ids'], chroma_result['embeddings'])}

    semantic_scored = []
    for candidate in filtered_candidates:
        emb = id_to_embedding.get(candidate['id'])
        if emb is not None:
            emb_arr = np.array(emb, dtype=np.float32)
            emb_norm = emb_arr / (np.linalg.norm(emb_arr) + 1e-10)
            sim = float(np.dot(query_norm, emb_norm))
        else:
            sim = 0.0
        semantic_scored.append((candidate, sim))

    semantic_scored.sort(key=lambda x: x[1], reverse=True)
    semantic_top = semantic_scored[:TOP_K_RETRIEVAL]
    semantic_top_ids = {c['id'] for c, _ in semantic_top}

    print(f"\n🔵 Semantic Top-{TOP_K_RETRIEVAL} (sur {len(filtered_candidates)} candidats filtrés):")
    for candidate, score in semantic_top:
        print(f"   SEM  {candidate['meta']['title'][:40]:40s} | Cosine: {score:.4f}")

    # --- Merge: union of both top-K sets ---
    merged_ids = bm25_top_ids | semantic_top_ids
    only_bm25 = bm25_top_ids - semantic_top_ids
    only_sem = semantic_top_ids - bm25_top_ids
    overlap = bm25_top_ids & semantic_top_ids
    merged_candidates = [c for c in filtered_candidates if c['id'] in merged_ids]

    print(f"\n🔀 Merge: {len(bm25_top_ids)} BM25 + {len(semantic_top_ids)} Semantic")
    print(f"   Overlap: {len(overlap)} | Only BM25: {len(only_bm25)} | Only Semantic: {len(only_sem)}")
    print(f"   → {len(merged_candidates)} candidats envoyés au CrossEncoder\n")

    # --- Rerank merged set with CrossEncoder ---
    pairs = [[query, c["content"]] for c in merged_candidates]
    scores = reranker.predict(pairs)

    print(f"🔍 DEBUG - Reranker Scores Statistics:")
    print(f"   Min score: {min(scores):.4f}")
    print(f"   Max score: {max(scores):.4f}")
    print(f"   Mean score: {sum(scores)/len(scores):.4f}\n")

    for candidate, score in zip(merged_candidates, scores):
        candidate['score'] = float(score)

    merged_candidates.sort(key=lambda x: x['score'], reverse=True)

    print(f"🏆 Ordre final après reranking:")
    for i, candidate in enumerate(merged_candidates, 1):
        print(f"   #{i:2d} {candidate['meta']['title'][:40]:40s} | Raw: {candidate['score']:7.4f}")

    return merged_candidates



def main():
    st.title("🎓 EPFL Course Recommender")
    st.markdown("### Trouve les cours qui matchent avec tes objectifs professionnels")
    st.markdown("---")

    # Load resources first
    emb, rerank, coll, bm25, data = load_resources()

    # Sidebar with improved design
    with st.sidebar:
        st.markdown("# 🔍 Filtres")
        st.markdown("Personnalise ta recherche de cours")
        st.markdown("---")

        # Section selection (combined list with level in parentheses)
        section_display_names = [entry[0] for entry in ALL_SECTIONS]
        selected_display = st.selectbox(
            "🎯 Section / Programme",
            section_display_names,
            help="Sélectionne ta section — le niveau (Bachelor/Master) est indiqué entre parenthèses"
        )

        # Derive level and section name from selection
        _, section, level = next(e for e in ALL_SECTIONS if e[0] == selected_display)

        # Dynamic semester options based on level
        if level == "Bachelor":
            semester_options = ["BA3", "BA4", "BA5", "BA6"]
        else:
            semester_options = ["MA1", "MA2", "MA3", "MA4"]

        semester_filter = st.selectbox(
            "📅 Semestre",
            semester_options,
        )

        course_type_filter = st.radio(
            "📌 Type de cours",
            ["Optionnel", "Obligatoire", "Tous"],
            index=0,
            horizontal=True,
        )

        st.markdown("---")

        # Reset button
        if st.button("🔄 Réinitialiser", use_container_width=True, help="Réinitialise la recherche"):
            st.session_state.query = ""
            st.rerun()

        filters = (level, section, semester_filter, course_type_filter)

        # Info section
        st.markdown("---")
        st.markdown("### 💡 Comment ça marche ?")
        st.markdown("""
        1. **Sélectionne** ta section (Bachelor/Master inclus)
        2. **Choisis** ton semestre
        3. **Décris** ton job de rêve
        4. **Découvre** les cours pertinents
        """)

    # Initialize session state for query
    if 'query' not in st.session_state:
        st.session_state.query = ""

    # Job example picker
    with st.expander("💼 Exemples d'offres d'emploi", expanded=False):
        example_keys = list(JOB_EXAMPLES.keys())
        selected_example = st.selectbox(
            "Sélectionne un profil de poste :",
            example_keys,
            index=0,
            label_visibility="collapsed",
        )
        if st.button("🪄 Appliquer cet exemple", use_container_width=True):
            st.session_state.query = JOB_EXAMPLES[selected_example]
            st.rerun()

    query = st.text_area(
        "📝 Décris le type de job ou de compétences que tu vises (optionnel)",
        value=st.session_state.query,
        height=200,
        placeholder="Ex: Je veux travailler en data science, faire du machine learning, analyser des données...\n\nOu colle une offre d'emploi complète.\n\nℹ️ Laisse vide pour voir tous les cours (ordre alphabétique)."
    )

    if st.button("🔍 Rechercher les cours", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyse des cours en cours..."):
            results = search_courses(query, filters, emb, rerank, coll, bm25, data)

        if not results:
            st.error("❌ Aucun cours trouvé pour cette section/semestre. Vérifie tes filtres.")
            return

        # Results header
        st.markdown("---")
        n = len(results)
        plural = "s" if n > 1 else ""
        if query and query.strip():
            st.success(f"✅ **{n} cour{plural} trouvé{plural}** (triés par pertinence)")
        else:
            st.info(f"📚 **{n} cour{plural} disponible{plural}** (ordre alphabétique)")

        st.markdown("")

        # Display results as stylized course cards
        for i, r in enumerate(results, 1):
            # Parse course metadata
            course_info = parse_course_metadata(r['content'])

            # Course card container
            with st.container():
                # Title with link and ranking badge
                col_rank, col_title = st.columns([0.5, 11.5])

                with col_rank:
                    st.markdown(f"### `{i}`")

                with col_title:
                    st.markdown(f"### [{r['meta']['title']}]({r['meta']['url']})")

                # Metadata badges in columns
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"**📋 Code**")
                    st.code(course_info['code'])

                with col2:
                    st.markdown(f"**🎓 Crédits**")
                    st.code(course_info['credits'])

                with col3:
                    st.markdown(f"**🏫 Section**")
                    st.code(r['section'][:20] + "..." if len(r['section']) > 20 else r['section'])

                with col4:
                    st.markdown(f"**📅 Semestre**")
                    st.code(r['semester'])

                # Professor and language in a second row
                col5, col6 = st.columns(2)

                with col5:
                    st.markdown(f"**👨‍🏫 Enseignant**")
                    st.caption(course_info['professor'])

                with col6:
                    st.markdown(f"**🌐 Langue**")
                    st.caption(course_info['language'])

                # Relevance score (only if query was provided)
                if query and query.strip():
                    raw_score = r.get('score', 0)
                    score_pct = calculate_score_percentage(raw_score)

                    # Debug print to terminal
                    print(f"🖥️  DEBUG Display - {r['meta']['title'][:30]:30s} | Raw: {raw_score:7.4f} | Display: {score_pct*100:5.1f}%")

                    st.markdown(f"**📊 Pertinence:** {score_pct*100:.1f}%")
                    st.progress(score_pct)

                # Description in expander
                with st.expander("📖 Voir la description et les détails du cours"):
                    # Display first 800 characters of content
                    content_preview = r['content'][:800]
                    if len(r['content']) > 800:
                        content_preview += "..."
                    st.markdown(content_preview)
                    st.markdown(f"[🔗 Voir la page complète du cours]({r['meta']['url']})")

                st.markdown("---")

if __name__ == "__main__":
    main()