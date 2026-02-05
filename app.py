from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from rank_bm25 import BM25Okapi
import streamlit as st
import math
import json

# CONST
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"

JOB_EXAMPLES = {
    "📊 Data Scientist": """Position: Senior Data Scientist
Location: Lausanne
We are looking for an expert in Machine Learning and Big Data.
Responsibilities:
- Build predictive models using Scikit-Learn, PyTorch, and TensorFlow.
- Process large datasets with Spark and Hadoop.
- Implement Natural Language Processing (NLP) pipelines.
- Strong background in Statistics, Probability, and Linear Algebra.""",

    "☁️ DevOps / Cloud": """Position: DevOps Engineer
Location: Zurich
Join our infrastructure team to scale our SaaS platform.
Skills Required:
- CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions).
- Container orchestration with Docker and Kubernetes (K8s).
- Infrastructure as Code (Terraform, Ansible).
- Cloud platforms: AWS (EC2, Lambda, S3) or Azure.
- Monitoring with Prometheus and Grafana.
- Scripting in Bash and Go.""",

    "🧬 Biomedical Eng.": """Position: R&D Biomedical Engineer
Location: Geneva
Design the next generation of medical devices.
Key Skills:
- Biosignal processing (EEG, ECG, EMG) using Matlab/Python.
- Biomechanics and prosthetics design.
- Regulatory standards (ISO 13485, FDA).
- Medical imaging analysis (MRI, CT-Scan).
- Microfluidics and Lab-on-a-chip technologies.""",

    "⚡ Electrical Eng.": """Position: Hardware / Electrical Engineer
Location: Neuchatel
Develop high-performance electronic systems.
Requirements:
- PCB Design and layout (Altium Designer, KiCad).
- FPGA programming (VHDL / Verilog).
- Embedded systems (C/C++, STM32, Microcontrollers).
- Signal processing and analog circuit design.
- Power electronics and battery management systems (BMS).""",

    "⚙️ Mechanical Eng.": """Position: Mechanical Design Engineer
Location: Bern
Focus on precision engineering and robotics.
Responsibilities:
- 3D CAD modeling (SolidWorks, CATIA, Siemens NX).
- Finite Element Analysis (FEA) and structural simulation (ANSYS).
- Thermodynamics and Heat Transfer analysis.
- Fluid mechanics and aerodynamics (CFD).
- Rapid prototyping and additive manufacturing.""",

    "🏗️ Civil Eng.": """Position: Structural Civil Engineer
Location: Fribourg
Design sustainable infrastructure and buildings.
Skills:
- Structural analysis of reinforced concrete and steel.
- Geotechnical engineering and soil mechanics.
- BIM (Building Information Modeling) with Revit or Civil 3D.
- Hydraulics and hydrology for urban water management.
- Environmental impact assessment.""",

    "🏛️ Architecture": """Position: Architect / Urban Planner
Location: Basel
Create innovative sustainable living spaces.
Skills:
- Architectural design and theory.
- Parametric design (Rhino, Grasshopper).
- Sustainable urban planning and landscape architecture.
- Heritage conservation and restoration.
- Graphic representation and rendering.""",

    "🧪 Materials Science": """Position: Materials R&D Engineer
Location: Sion
Develop novel materials for energy applications.
Skills:
- Characterization techniques (SEM, XRD, Spectroscopy).
- Polymer science and composite materials.
- Metallurgy and ceramics.
- Nanotechnology and surface functionalization.
- Photovoltaics and semiconductor physics."""
}

st.set_page_config("EPFL Course Recommender", page_icon="🎓", layout="wide")

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
@st.cache_resource
def load_resources():

    # Models
    embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    # DB
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    all_docs = collection.get()

    tokenized_corpus = [doc.split() for doc in all_docs['documents']]
    bm25 = BM25Okapi(tokenized_corpus)

    return embedder, reranker, collection, bm25, all_docs


def search_courses(query, filters, embedder, reranker, collection, bm25, all_data, top_k=10):
    query_emb = embedder.encode(query).tolist()
    ia_candidates = collection.query(query_embeddings=[query_emb], n_results = top_k * 2)
    ia_ids = set(ia_candidates['ids'][0])

    # We have candidates based on scalar products. Now we will filter again
    # With BM25, based on key words
    bm25_candidates = bm25.get_top_n(query.split(), all_data['documents'], n=top_k * 2)
    bm25_ids = set(bm25_candidates)

    # Filtering
    for doc in bm25_candidates:
        idx = all_data['documents'].index(doc)
        bm25_ids.add(all_data['ids'][idx])
    
    combined_ids = ia_ids.union(bm25_ids)

    filtered_candidates = []
    target_aliases, target_level = filters

    print(f"\n{'='*80}")
    print(f"🔍 FILTRES ACTIFS: target_aliases={target_aliases}, target_level={target_level}")
    print(f"📊 Nombre de candidats combinés: {len(combined_ids)}")
    print(f"{'='*80}\n")

    for cid in combined_ids:
        if cid not in all_data['ids']: continue
        dbIdx = all_data['ids'].index(cid)
        meta = all_data['metadatas'][dbIdx]
        plans = json.loads(meta.get('metadata', '[]'))

        print(f"\n--- Cours ID: {cid} | Titre: {meta.get('title', 'N/A')[:50]}... ---")
        print(f"Plans trouvés: {plans}")

        isMatch = False
        badge = ""

        if target_aliases is None:
            isMatch = True
            print(f"✓ Mode 'Tout explorer' - isMatch=True")
        else:
            for i, p in enumerate(plans):
                sec = p.get('section', '').lower()
                lvl = p.get('level', '').lower()

                sec_match = any(alias.lower() in sec for alias in target_aliases)
                lvl_match = target_level.lower() in lvl

                print(f"  Plan {i+1}: section='{sec}', level='{lvl}'")
                print(f"    → sec_match={sec_match}, lvl_match={lvl_match}")

                if sec_match and lvl_match:
                    isMatch = True
                    badge = "Obligatoire" if p.get('isMandatory') else "Optionnel"
                    print(f"    ✓ MATCH TROUVÉ ! Badge: {badge}")
                    break

        print(f"Résultat final: isMatch={isMatch}")

        if isMatch:
            filtered_candidates.append(
                {
                    "id": cid,
                    "content": all_data['documents'][dbIdx],
                    "meta": meta,
                    "badge": badge
                }
            )
    # Remove duplicates
    unique_titles = set()
    unique_candidates = []
    for candidate in filtered_candidates:
        title = candidate['meta']['title']
        if title not in unique_titles:
            unique_candidates.append(candidate)
            unique_titles.add(title)
    filtered_candidates = unique_candidates

    if not filtered_candidates: return []

    # Reranking
    #Preparing (Query, Document) pairs for CrossEncoder
    pairs = [[query, candidate["content"]] for candidate in filtered_candidates]
    scores = reranker.predict(pairs)

    for candidate, score in zip(filtered_candidates, scores):
        candidate['score'] = score
    filtered_candidates.sort(key=lambda x: x['score'], reverse = True)

    return filtered_candidates[:top_k]



def main():
    st.title("EPFL Course Matcher 🎓")

    # Sidebar
    with st.sidebar:
        st.header("Filtres")
        degree_selected = st.selectbox("Diplôme", list(PROGRAMMES.keys()))
        filters = PROGRAMMES[degree_selected]
        k = st.slider("Nombre de résultats", 1, 10, 5)

    emb, rerank, coll, bm25, data = load_resources()

    # Initialize session state for query
    if 'query' not in st.session_state:
        st.session_state.query = ""

    # Example buttons (2 rows of 4)
    st.markdown("**Exemples de test :**")
    examples_list = list(JOB_EXAMPLES.items())

    # First row (4 buttons)
    cols1 = st.columns(4)
    for i in range(4):
        if i < len(examples_list):
            label, example_text = examples_list[i]
            with cols1[i]:
                if st.button(label, use_container_width=True, key=f"btn_{i}"):
                    st.session_state.query = example_text

    # Second row (4 buttons)
    cols2 = st.columns(4)
    for i in range(4, 8):
        if i < len(examples_list):
            label, example_text = examples_list[i]
            with cols2[i-4]:
                if st.button(label, use_container_width=True, key=f"btn_{i}"):
                    st.session_state.query = example_text

    query = st.text_area("Colle une offre d'emploi que tu vises", value=st.session_state.query, height=200)

    if st.button("Rechercher"):
        if not query:
            st.warning("écris quelque chose !")
            return
        with st.spinner("Analyse en cours..."):
            results = search_courses(query, filters, emb, rerank, coll, bm25, data, k)

        for r in results:
            score_percent =  1 / (1 + math.exp(-(r['score'] + 6)))
            color = "red" if r['badge'] == "Obligatoire" else "green"
            st.markdown(f"### [{r['meta']['title']}]({r['meta']['url']}) - **{score_percent*100:.1f}% match**")
            st.progress(score_percent)
            with st.expander("Voir plus"):
                st.write(r['content'][:400] + "...")

if __name__ == "__main__":
    main()