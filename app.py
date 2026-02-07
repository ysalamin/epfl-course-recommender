from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from rank_bm25 import BM25Okapi
import streamlit as st
import math
import json

# CONST
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"

# Allowlist for sections (Bachelor + Master)
ALLOWED_SECTIONS_BACHELOR = [
    'Architecture', 'Chimie', 'Chimie et génie chimique', 'Génie chimique',
    'Génie civil', 'Génie mécanique', 'Génie électrique et électronique',
    'Informatique', 'Ingénierie des sciences du vivant', 'Mathématiques',
    'Microtechnique', 'Physique', 'Science et génie des matériaux',
    'Sciences et ingénierie de l\'environnement', 'Systèmes de communication'
]

ALLOWED_SECTIONS_MASTER = [
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

# Union of both lists (sorted alphabetically)
ALLOWED_SECTIONS = sorted(list(set(ALLOWED_SECTIONS_BACHELOR + ALLOWED_SECTIONS_MASTER)))

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
def get_filtered_sections(all_data):
    """Extract unique sections from metadata, filtered by allowlist"""
    sections = set()

    for meta in all_data['metadatas']:
        plans = json.loads(meta.get('metadata', '[]'))
        for plan in plans:
            section = plan.get('section', '').strip()
            # Only include sections that are in the allowlist
            if section in ALLOWED_SECTIONS:
                sections.add(section)

    return sorted(list(sections))


def search_courses(query, filters, embedder, reranker, collection, bm25, all_data):
    """
    New logic: Show ALL courses matching filters, sorted by relevance
    - First: Apply strict filters (level, section, semester, type='Optionnel')
    - Then: Calculate relevance score for ALL filtered courses
    - Finally: Sort by relevance (query only affects ORDER, not visibility)
    """
    target_level, target_section, semester_filter = filters

    print(f"\n{'='*80}")
    print(f"FILTRES: level={target_level}, section={target_section}, semester={semester_filter}")
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

    print(f"\nCours optionnels trouvés (TOTAL): {len(filtered_candidates)}\n")

    if not filtered_candidates:
        return []

    # Step 2: Calculate relevance score for ALL filtered courses
    if query and query.strip():
        print("Calcul des scores de pertinence pour TOUS les cours...\n")
        pairs = [[query, candidate["content"]] for candidate in filtered_candidates]
        scores = reranker.predict(pairs)

        for candidate, score in zip(filtered_candidates, scores):
            candidate['score'] = score

        # Sort by relevance score (highest first)
        filtered_candidates.sort(key=lambda x: x['score'], reverse=True)
    else:
        # No query: sort alphabetically by title
        filtered_candidates.sort(key=lambda x: x['meta']['title'])
        for candidate in filtered_candidates:
            candidate['score'] = 0  # Neutral score

    return filtered_candidates  # Return ALL matching courses



def main():
    st.title("EPFL Course Matcher 🎓")
    st.markdown("**Trouve les cours optionnels qui matchent avec tes objectifs professionnels**")

    # Load resources first
    emb, rerank, coll, bm25, data = load_resources()

    # Sidebar
    with st.sidebar:
        st.header("Filtres")

        # Semester selection (implicitly determines level)
        semester_choice = st.selectbox(
            "Semestre",
            ["BA3", "BA4", "BA5", "BA6", "MA"],
            help="BA = Bachelor, MA = Master"
        )

        # Derive level and semester_filter from semester choice
        if semester_choice == "MA":
            level = "Master"
            semester_filter = None  # No semester filtering for Master
        else:
            level = "Bachelor"
            # Map BA semesters to Fall/Spring
            if semester_choice in ["BA3", "BA5"]:
                semester_filter = "Fall"
            else:  # BA4, BA6
                semester_filter = "Spring"

        # Show derived information
        if semester_filter:
            st.info(f"📚 **{level}**\n📅 Semestre: {semester_filter}")
        else:
            st.info(f"📚 **{level}**")

        # Section selection (filtered by allowlist)
        available_sections = get_filtered_sections(data)

        if not available_sections:
            st.error("Aucune section disponible dans les données")
            section = None
        else:
            section = st.selectbox(
                "Section / Programme",
                available_sections,
                help="Sections filtrées selon le programme officiel EPFL"
            )

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
        "📝 Décris le type de job ou de compétences que tu vises (optionnel)",
        value=st.session_state.query,
        height=200,
        placeholder="Ex: Je veux travailler en data science, faire du machine learning, analyser des données...\n\nOu colle une offre d'emploi complète.\n\nℹ️ Laisse vide pour voir tous les cours (ordre alphabétique)."
    )

    if st.button("Afficher les cours", type="primary", use_container_width=True):
        with st.spinner("Chargement des cours optionnels..."):
            results = search_courses(query, filters, emb, rerank, coll, bm25, data)

        if not results:
            st.error("Aucun cours optionnel trouvé pour cette section/semestre. Vérifie tes filtres.")
            return

        if query and query.strip():
            st.success(f"✅ {len(results)} cours optionnel{'s' if len(results) > 1 else ''} (triés par pertinence)")
        else:
            st.info(f"📚 {len(results)} cours optionnel{'s' if len(results) > 1 else ''} disponible{'s' if len(results) > 1 else ''} (ordre alphabétique)")

        for i, r in enumerate(results, 1):
            # Display course with ranking (score hidden, but order preserved)
            st.markdown(f"### {i}. [{r['meta']['title']}]({r['meta']['url']})")
            st.markdown(f"**🎓 {r['section']}** | **📅 {r['semester']}** | ⭐ Cours Optionnel")

            with st.expander("📖 Voir le contenu du cours"):
                st.write(r['content'][:500] + "...")

            st.markdown("---")

if __name__ == "__main__":
    main()