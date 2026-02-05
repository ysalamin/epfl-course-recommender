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


@st.cache_data
def get_unique_sections(all_data):
    """Extract all unique sections from the metadata"""
    sections = set()

    for meta in all_data['metadatas']:
        plans = json.loads(meta.get('metadata', '[]'))
        for plan in plans:
            section = plan.get('section', '').strip()
            if section and section.lower() not in ['unknown', '', 'autre']:
                sections.add(section)

    return sorted(list(sections))


def search_courses(query, filters, embedder, reranker, collection, bm25, all_data):
    """
    Strict filtering logic:
    - Filter by level (Bachelor/Master)
    - Filter by section (user's program)
    - Filter by type == 'Optionnel' ONLY
    - If Bachelor, filter by semester (Fall/Spring)
    - Return ALL matching courses sorted by relevance
    """
    target_level, target_section, semester_filter = filters

    # Get more candidates to ensure we don't miss relevant optional courses
    query_emb = embedder.encode(query).tolist()
    ia_candidates = collection.query(query_embeddings=[query_emb], n_results=100)
    ia_ids = set(ia_candidates['ids'][0])

    # BM25 keyword search
    bm25_candidates = bm25.get_top_n(query.split(), all_data['documents'], n=100)
    bm25_ids = set()
    for doc in bm25_candidates:
        idx = all_data['documents'].index(doc)
        bm25_ids.add(all_data['ids'][idx])

    combined_ids = ia_ids.union(bm25_ids)

    print(f"\n{'='*80}")
    print(f"FILTRES: level={target_level}, section={target_section}, semester={semester_filter}")
    print(f"Candidats initiaux: {len(combined_ids)}")
    print(f"{'='*80}\n")

    filtered_candidates = []

    for cid in combined_ids:
        if cid not in all_data['ids']: continue
        dbIdx = all_data['ids'].index(cid)
        meta = all_data['metadatas'][dbIdx]
        plans = json.loads(meta.get('metadata', '[]'))

        # Check if ANY plan matches our criteria
        for plan in plans:
            lvl = plan.get('level', '')
            sec = plan.get('section', '').strip()
            course_type = plan.get('type', '')
            sem = plan.get('semester', '')

            # Strict filtering
            level_match = (lvl == target_level)
            section_match = (sec == target_section)  # CRITICAL: Section must match
            type_match = (course_type == "Optionnel")

            # Semester match (only for Bachelor)
            if target_level == "Bachelor":
                semester_match = (sem == semester_filter)
            else:
                semester_match = True  # No semester filter for Master

            if level_match and section_match and type_match and semester_match:
                print(f"✓ MATCH: {meta.get('title', 'N/A')[:50]} | {lvl} | {sec} | {course_type} | {sem}")
                filtered_candidates.append({
                    "id": cid,
                    "content": all_data['documents'][dbIdx],
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

    print(f"\nCours optionnels trouvés après filtrage strict: {len(filtered_candidates)}\n")

    if not filtered_candidates:
        return []

    # Reranking by relevance to job description
    pairs = [[query, candidate["content"]] for candidate in filtered_candidates]
    scores = reranker.predict(pairs)

    for candidate, score in zip(filtered_candidates, scores):
        candidate['score'] = score

    filtered_candidates.sort(key=lambda x: x['score'], reverse=True)

    return filtered_candidates  # Return ALL matching courses



def main():
    st.title("EPFL Course Matcher 🎓")
    st.markdown("**Trouve les cours optionnels qui matchent avec tes objectifs professionnels**")

    # Load resources first
    emb, rerank, coll, bm25, data = load_resources()

    # Sidebar
    with st.sidebar:
        st.header("Filtres")

        # Level selection
        level = st.radio("Niveau d'études", ["Bachelor", "Master"], index=0)

        # Section selection (dynamic from data)
        available_sections = get_unique_sections(data)
        section = st.selectbox(
            "Section / Programme",
            available_sections,
            help="Choisissez votre section d'études"
        )

        # Semester selection (only for Bachelor)
        semester_filter = None
        if level == "Bachelor":
            ba_semester = st.selectbox(
                "Semestre actuel",
                ["BA1", "BA2", "BA3", "BA4", "BA5", "BA6"]
            )
            # Map to Fall/Spring
            if ba_semester in ["BA1", "BA3", "BA5"]:
                semester_filter = "Fall"
            else:  # BA2, BA4, BA6
                semester_filter = "Spring"

            st.info(f"📅 Cours du semestre: {semester_filter}")

        filters = (level, section, semester_filter)

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

    query = st.text_area(
        "📝 Décris le type de job ou de compétences que tu vises",
        value=st.session_state.query,
        height=200,
        placeholder="Ex: Je veux travailler en data science, faire du machine learning, analyser des données...\n\nOu colle une offre d'emploi complète."
    )

    if st.button("Rechercher", type="primary", use_container_width=True):
        if not query:
            st.warning("Décris d'abord tes objectifs professionnels !")
            return
        with st.spinner("Recherche des cours optionnels correspondants..."):
            results = search_courses(query, filters, emb, rerank, coll, bm25, data)

        if not results:
            st.error("Aucun cours optionnel trouvé avec ces critères. Essaie un autre semestre ou niveau.")
            return

        st.success(f"✅ {len(results)} cours optionnel{'s' if len(results) > 1 else ''} trouvé{'s' if len(results) > 1 else ''}")

        for i, r in enumerate(results, 1):
            score_percent = 1 / (1 + math.exp(-(r['score'] + 6)))

            # Display course with ranking
            st.markdown(f"### {i}. [{r['meta']['title']}]({r['meta']['url']}) - **{score_percent*100:.1f}% match**")
            st.markdown(f"**🎓 {r['section']}** | **📅 {r['semester']}** | ⭐ Cours Optionnel")
            st.progress(score_percent)

            with st.expander("📖 Voir le contenu du cours"):
                st.write(r['content'][:500] + "...")

            st.markdown("---")

if __name__ == "__main__":
    main()