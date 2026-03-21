# CRITICAL: Patch SQLite for ChromaDB on Streamlit Cloud (Linux)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # Windows/local environment - use standard sqlite3
    pass

import streamlit as st
from job_examples import JOB_EXAMPLES
from core.utils import ALL_SECTIONS, parse_course_metadata, calculate_score_percentage
from core.database import load_resources
from core.search import search_courses

# Must be first Streamlit command
st.set_page_config(
    page_title="EPFL Course Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.title("🎓 EPFL Course Recommender")
    st.markdown("### Trouve les cours qui matchent avec tes objectifs professionnels")
    st.markdown("---")

    emb, coll, bm25, data = load_resources()

    with st.sidebar:
        st.markdown("# 🔍 Filtres")
        st.markdown("Personnalise ta recherche de cours")
        st.markdown("---")

        section_display_names = [entry[0] for entry in ALL_SECTIONS]
        selected_display = st.selectbox(
            "🎯 Section / Programme",
            section_display_names,
            help="Sélectionne ta section — le niveau (Bachelor/Master) est indiqué entre parenthèses"
        )

        _, section, level = next(e for e in ALL_SECTIONS if e[0] == selected_display)

        semester_options = ["BA3", "BA4", "BA5", "BA6"] if level == "Bachelor" else ["MA1", "MA2", "MA3", "MA4"]

        semester_filter = st.selectbox("📅 Semestre", semester_options)

        course_type_filter = st.radio(
            "📌 Type de cours",
            ["Optionnel", "Obligatoire", "Tous"],
            index=0,
            horizontal=True,
        )

        st.markdown("---")

        if st.button("🔄 Réinitialiser", use_container_width=True, help="Réinitialise la recherche"):
            st.session_state.query = ""
            st.rerun()

        filters = (level, section, semester_filter, course_type_filter)

        st.markdown("---")
        st.markdown("### 💡 Comment ça marche ?")
        st.markdown("""
        1. **Sélectionne** ta section (Bachelor/Master inclus)
        2. **Choisis** ton semestre
        3. **Décris** ton job de rêve
        4. **Découvre** les cours pertinents
        """)

    if 'query' not in st.session_state:
        st.session_state.query = ""
    if 'llm_search_count' not in st.session_state:
        st.session_state.llm_search_count = 0

    def apply_job_example():
        key = st.session_state.job_example_selector
        if key:
            st.session_state.query = JOB_EXAMPLES[key]

    st.selectbox(
        "💼 Exemple d'offre d'emploi",
        options=[""] + list(JOB_EXAMPLES.keys()),
        index=0,
        key="job_example_selector",
        on_change=apply_job_example,
        format_func=lambda x: "-- Sélectionne un exemple --" if x == "" else x,
    )

    query = st.text_area(
        "📝 Décris le type de job ou de compétences que tu vises (optionnel)",
        value=st.session_state.query,
        height=200,
        placeholder=(
            "Ex: Je veux travailler en data science, faire du machine learning, analyser des données...\n\n"
            "Ou colle une offre d'emploi complète.\n\n"
            "ℹ️ Laisse vide pour voir tous les cours (ordre alphabétique)."
        )
    )

    if st.button("🔍 Rechercher les cours", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyse des cours en cours..."):
            results = search_courses(query, filters, emb, coll, bm25, data)

        if not results:
            st.error("❌ Aucun cours trouvé pour cette section/semestre. Vérifie tes filtres.")
            return

        st.markdown("---")
        n = len(results)
        plural = "s" if n > 1 else ""
        if query and query.strip():
            st.success(f"✅ **{n} cour{plural} trouvé{plural}** (triés par pertinence)")
        else:
            st.info(f"📚 **{n} cour{plural} disponible{plural}** (ordre alphabétique)")

        st.markdown("")

        for i, r in enumerate(results, 1):
            course_info = parse_course_metadata(r['content'])

            with st.container():
                col_rank, col_title = st.columns([0.5, 11.5])
                with col_rank:
                    st.markdown(f"### `{i}`")
                with col_title:
                    st.markdown(f"### [{r['meta']['title']}]({r['meta']['url']})")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("**📋 Code**")
                    st.code(course_info['code'])
                with col2:
                    st.markdown("**🎓 Crédits**")
                    st.code(course_info['credits'])
                with col3:
                    st.markdown("**🏫 Section**")
                    st.code(r['section'][:20] + "..." if len(r['section']) > 20 else r['section'])
                with col4:
                    st.markdown("**📅 Semestre**")
                    st.code(r['semester'])

                col5, col6 = st.columns(2)
                with col5:
                    st.markdown("**👨‍🏫 Enseignant**")
                    st.caption(course_info['professor'])
                with col6:
                    st.markdown("**🌐 Langue**")
                    st.caption(course_info['language'])

                if query and query.strip():
                    score_pct = calculate_score_percentage(r)
                    st.markdown(f"**📊 Pertinence:** {score_pct*100:.1f}%")
                    st.progress(score_pct)

                with st.expander("📖 Voir la description et les détails du cours"):
                    content_preview = r['content'][:800]
                    if len(r['content']) > 800:
                        content_preview += "..."
                    st.markdown(content_preview)
                    st.markdown(f"[🔗 Voir la page complète du cours]({r['meta']['url']})")

                st.markdown("---")


if __name__ == "__main__":
    main()
