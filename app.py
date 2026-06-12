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
from core.utils import (
    ALL_SECTIONS, SECTION_LANGUAGE_MAPPING, COURSE_TYPE_MAP,
    parse_course_metadata, calculate_score_percentage,
)
from core.database import load_resources
from core.search import search_courses

# Must be first Streamlit command
st.set_page_config(
    page_title="EPFL Course Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Compact layout: reduce default top-padding and element gaps
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
div[data-testid="stVerticalBlock"] > div { gap: 0.25rem; }
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown("## 🎓 EPFL Course Recommender")
    st.caption("Find courses that match your interests and career goals")

    emb, coll, bm25, data = load_resources()

    # ── Steps 1 / 2 / 3 — Filters ───────────────────────────────────────────
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        st.markdown("**1️⃣ Choose your section**")
        section_display_names = [entry[0] for entry in ALL_SECTIONS]
        _default_section_idx = next(
            (i for i, e in enumerate(ALL_SECTIONS) if e[1] == "Computer Science" and e[2] == "Bachelor"),
            0,
        )
        selected_display = st.selectbox(
            "Section / Programme",
            section_display_names,
            index=_default_section_idx,
            help="Select your section — the level (Bachelor/Master) is shown in parentheses",
            label_visibility="collapsed",
        )

    _, section, level = next(e for e in ALL_SECTIONS if e[0] == selected_display)

    with filter_col2:
        st.markdown("**2️⃣ Pick your semester**")
        semester_options = ["BA3", "BA4", "BA5", "BA6"] if level == "Bachelor" else ["Fall", "Spring"]
        semester_filter = st.selectbox(
            "Semester",
            semester_options,
            help="Bachelor: specific semester (BA3–BA6). Master: Fall (MA1/MA3) or Spring (MA2/MA4).",
            label_visibility="collapsed",
        )

    with filter_col3:
        st.markdown("**3️⃣ Course type**")
        _course_type_options = ["Optional", "Mandatory", "All", "Out-of-plan"]
        course_type_filter = st.radio(
            "Course Type",
            _course_type_options,
            index=_course_type_options.index("All"),
            horizontal=True,
            help=(
                "**Out-of-plan**: shows same-level courses from *other* sections "
                "matching the selected semester parity (any type)."
            ),
            label_visibility="collapsed",
        )

    filters = (level, SECTION_LANGUAGE_MAPPING[section], semester_filter, COURSE_TYPE_MAP[course_type_filter])

    # ── Step 4 — Job description ─────────────────────────────────────────────
    st.markdown("**4️⃣ Describe your dream job (or pick an example)**")

    if 'query' not in st.session_state:
        st.session_state.query = ""
    if 'llm_search_count' not in st.session_state:
        st.session_state.llm_search_count = 0

    def apply_job_example():
        key = st.session_state.job_example_selector
        if key:
            st.session_state.query = JOB_EXAMPLES[key]

    st.selectbox(
        "💼 Job Description Example",
        options=[""] + list(JOB_EXAMPLES.keys()),
        index=0,
        key="job_example_selector",
        on_change=apply_job_example,
        format_func=lambda x: "-- Select an example --" if x == "" else x,
    )

    query = st.text_area(
        "📝 Describe what interests you or paste a job posting",
        value=st.session_state.query,
        height=200,
        placeholder=(
            "Ex: I like math, cryptography, and optimization...\n\n"
            "Or paste a full job posting.\n\n"
            "ℹ️ Leave empty to browse all courses (alphabetical order)."
        )
    )

    # ── Step 5 — Search ──────────────────────────────────────────────────────
    if st.button("🔍 Search courses", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyzing courses..."):
            results = search_courses(query, filters, emb, coll, bm25, data)

        if not results:
            st.error("❌ No courses found for this section/semester. Check your filters.")
            return

        st.markdown("---")
        n = len(results)
        plural = "s" if n > 1 else ""
        if query and query.strip():
            st.success(f"✅ **{n} course{plural} found** (sorted by relevance)")
        else:
            st.info(f"📚 **{n} course{plural} available** (alphabetical order)")

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
                    st.markdown("**🎓 Credits**")
                    st.code(course_info['credits'])
                with col3:
                    st.markdown("**🏫 Section**")
                    st.code(r['section'][:20] + "..." if len(r['section']) > 20 else r['section'])
                with col4:
                    st.markdown("**📅 Semester**")
                    st.code(r['semester'])

                col5, col6 = st.columns(2)
                with col5:
                    st.markdown("**👨‍🏫 Instructor**")
                    st.caption(course_info['professor'])
                with col6:
                    st.markdown("**🌐 Language**")
                    st.caption(course_info['language'])

                if query and query.strip():
                    score_pct = calculate_score_percentage(r)
                    st.markdown(f"**📊 Relevance:** {score_pct*100:.1f}%")
                    st.progress(score_pct)
                    reason = r.get('llm_reason', '')
                    if reason:
                        st.caption(f"💡 {reason}")

                with st.expander("📖 View course description and details"):
                    content_preview = r['content'][:800]
                    if len(r['content']) > 800:
                        content_preview += "..."
                    st.markdown(content_preview)
                    st.markdown(f"[🔗 View full course page]({r['meta']['url']})")

                st.markdown("---")

    # ── Sidebar — Help + Reset ───────────────────────────────────────────────
    with st.sidebar:
        if st.button("🔄 Reset", use_container_width=True, help="Reset the search"):
            st.session_state.query = ""
            st.rerun()

        st.divider()
        st.markdown("### ⚙️ How does it work?")
        st.markdown("""
1. **Select** your section (Bachelor/Master included)
2. **Pick** your semester
3. **Paste** a job description or keywords
4. **Hit Search** — courses ranked by relevance
        """)
        st.divider()
        st.markdown("### 💡 Tips")
        st.markdown("""
- Paste a **real job posting** for best results
- Leave the description **empty** to browse all courses alphabetically
- Try **Out-of-plan** to discover courses from other sections
- Shorter, focused queries often beat long paragraphs
        """)
        st.divider()
        st.markdown(
            "**ℹ️ About**\n\n"
            "Built for EPFL students to find courses matching their interests and career goals. "
            "Under the hood: semantic search over course embeddings, keyword matching, and AI-powered ranking.\n\n"
            "📩 Got a suggestion? Reach out: "
            "[yoann.salamin@epfl.ch](mailto:yoann.salamin@epfl.ch)"
        )


if __name__ == "__main__":
    main()
