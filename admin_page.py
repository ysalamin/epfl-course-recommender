import hmac
import os
import sqlite3
from datetime import datetime, timezone, timedelta

import pandas as pd
import streamlit as st

from core.analytics import get_db_path


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_admin_password() -> str | None:
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        pass
    return os.environ.get("ADMIN_PASSWORD")


def check_password(entered: str, expected: str) -> bool:
    return hmac.compare_digest(entered.encode(), expected.encode())


# ── Auth ─────────────────────────────────────────────────────────────────────

admin_pwd = get_admin_password()
if admin_pwd is None:
    st.error("Admin password not configured. Set ADMIN_PASSWORD in secrets or environment.")
    st.stop()

if not st.session_state.get("admin_authenticated"):
    st.title("📊 Admin — Analytics")
    pwd = st.text_input("Password", type="password", key="admin_pwd_input")
    if pwd:
        if check_password(pwd, admin_pwd):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


# ── Data loading (cached) ─────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    db = get_db_path()
    conn = sqlite3.connect(db, timeout=10)
    try:
        sessions_df = pd.read_sql_query("SELECT * FROM sessions", conn)
        searches_df = pd.read_sql_query("SELECT * FROM searches", conn)
    finally:
        conn.close()

    for df in (sessions_df, searches_df):
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")

    return sessions_df, searches_df


# ── Dashboard ────────────────────────────────────────────────────────────────

st.title("📊 Admin — Analytics")

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Refresh"):
        load_data.clear()
        st.rerun()

sessions_df, searches_df = load_data()

today_utc = datetime.now(timezone.utc).date()

# ── Top metrics ───────────────────────────────────────────────────────────────

total_sessions = len(sessions_df)
sessions_today = (
    (sessions_df["created_at"].dt.date == today_utc).sum()
    if not sessions_df.empty else 0
)
total_searches = len(searches_df)
searches_today = (
    (searches_df["created_at"].dt.date == today_utc).sum()
    if not searches_df.empty else 0
)
avg_duration = (
    int(searches_df["duration_ms"].mean())
    if not searches_df.empty and searches_df["duration_ms"].notna().any()
    else 0
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total sessions", total_sessions)
m2.metric("Sessions today", sessions_today)
m3.metric("Total searches", total_searches)
m4.metric("Searches today", searches_today)
m5.metric("Avg duration (ms)", avg_duration)

st.divider()

if searches_df.empty:
    st.info("No search data yet. Start using the app to see analytics here.")
    st.stop()

# ── Date helpers ─────────────────────────────────────────────────────────────

cutoff_30d = pd.Timestamp(today_utc - timedelta(days=29), tz="UTC")

# ── Charts row 1 : sessions / searches per day ───────────────────────────────

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Sessions per day (last 30 days)")
    if not sessions_df.empty:
        s30 = sessions_df[sessions_df["created_at"] >= cutoff_30d].copy()
        if not s30.empty:
            s30["day"] = s30["created_at"].dt.date
            daily_sessions = (
                s30.groupby("day").size().rename("Sessions")
                .reindex(pd.date_range(cutoff_30d.date(), today_utc, freq="D").date, fill_value=0)
            )
            st.bar_chart(daily_sessions)
        else:
            st.caption("No sessions in the last 30 days.")
    else:
        st.caption("No session data.")

with col_b:
    st.markdown("#### Searches per day (last 30 days)")
    sr30 = searches_df[searches_df["created_at"] >= cutoff_30d].copy()
    if not sr30.empty:
        sr30["day"] = sr30["created_at"].dt.date
        daily_searches = (
            sr30.groupby("day").size().rename("Searches")
            .reindex(pd.date_range(cutoff_30d.date(), today_utc, freq="D").date, fill_value=0)
        )
        st.bar_chart(daily_searches)
    else:
        st.caption("No searches in the last 30 days.")

# ── Charts row 2 : by section / course type ──────────────────────────────────

col_c, col_d = st.columns(2)

with col_c:
    st.markdown("#### Searches by section (top 10)")
    by_section = searches_df["section"].value_counts().head(10).rename("Searches")
    if not by_section.empty:
        st.bar_chart(by_section)
    else:
        st.caption("No section data.")

with col_d:
    st.markdown("#### Searches by course type")
    by_type = searches_df["course_type"].value_counts().rename("Searches")
    if not by_type.empty:
        st.bar_chart(by_type)
    else:
        st.caption("No course type data.")

# ── LLM rerank stats ─────────────────────────────────────────────────────────

st.divider()
st.markdown("#### LLM rerank usage")

total = len(searches_df)
llm_used = int(searches_df["used_llm_rerank"].sum()) if "used_llm_rerank" in searches_df else 0
llm_failed = int(searches_df["llm_rerank_failed"].sum()) if "llm_rerank_failed" in searches_df else 0

r1, r2, r3 = st.columns(3)
r1.metric("Searches with LLM rerank", llm_used, f"{llm_used/total*100:.1f}%" if total else "—")
r2.metric("LLM rerank failures", llm_failed, f"{llm_failed/total*100:.1f}%" if total else "—")
r3.metric("Searches without LLM", total - llm_used)

# ── Recent searches table ─────────────────────────────────────────────────────

st.divider()
st.markdown("#### Last 50 searches")

display_cols = ["created_at", "query", "section", "semester", "course_type", "num_results", "duration_ms"]
recent = searches_df.sort_values("created_at", ascending=False).head(50)[display_cols].copy()
recent["query"] = recent["query"].str.slice(0, 80)
recent["created_at"] = recent["created_at"].dt.strftime("%Y-%m-%d %H:%M UTC")
st.dataframe(recent, use_container_width=True, hide_index=True)

# ── CSV export ────────────────────────────────────────────────────────────────

st.divider()

csv_bytes = searches_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download full CSV",
    data=csv_bytes,
    file_name=f"searches_{today_utc}.csv",
    mime="text/csv",
)
