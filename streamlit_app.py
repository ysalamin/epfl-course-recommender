# CRITICAL: Patch SQLite for ChromaDB on Streamlit Cloud (Linux)
# Must run before any import that touches sqlite3 / chromadb / pysqlite3.
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # Windows / local environment — standard sqlite3 is fine
    pass

import streamlit as st

st.set_page_config(
    page_title="EPFL Course Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

main_page = st.Page("main_app.py", title="EPFL Course Recommender", icon="🎓", default=True)
admin_page = st.Page("admin_page.py", title="Admin", url_path="admin")

pg = st.navigation([main_page, admin_page], position="hidden")
pg.run()
