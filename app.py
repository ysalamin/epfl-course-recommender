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


def main():
    st.title("🎓 EPFL Course Recommender")
    st.markdown("### Find courses that match your interests and career goals")
    st.markdown("---")

    emb, coll, bm25, data = load_resources()

    with st.sidebar:
        st.markdown("# 🔍 Filters")
        st.markdown("Customize your course search")
        st.markdown("---")

        section_display_names = [entry[0] for entry in ALL_SECTIONS]
        selected_display = st.selectbox(
            "🎯 Section / Programme",
            section_display_names,
            help="Select your section — the level (Bachelor/Master) is shown in parentheses"
        )

        _, section, level = next(e for e in ALL_SECTIONS if e[0] == selected_display)

        semester_options = ["BA3", "BA4", "BA5", "BA6"] if level == "Bachelor" else ["Fall", "Spring"]

        semester_filter = st.selectbox(
            "📅 Semester",
            semester_options,
            help="Bachelor: specific semester (BA3–BA6). Master: Fall (MA1/MA3) or Spring (MA2/MA4).",
        )

        course_type_filter = st.radio(
            "📌 Course Type",
            ["Optional", "Mandatory", "All", "Out-of-plan"],
            index=0,
            horizontal=True,
            help=(
                "**Out-of-plan**: shows same-level courses from *other* sections "
                "matching the selected semester parity (any type)."
            ),
        )

        st.markdown("---")

        if st.button("🔄 Reset", use_container_width=True, help="Reset the search"):
            st.session_state.query = ""
            st.rerun()

        filters = (level, SECTION_LANGUAGE_MAPPING[section], semester_filter, COURSE_TYPE_MAP[course_type_filter])

        st.markdown("---")
        st.markdown("### 💡 How does it work?")
        st.markdown("""
        1. **Select** your section (Bachelor/Master included)
        2. **Choose** your semester
        3. **Describe** your dream job
        4. **Discover** relevant courses
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


if __name__ == "__main__":
    main()
