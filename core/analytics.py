import os
import sqlite3
import logging
import uuid
from datetime import datetime, timezone

import streamlit as st

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    return os.environ.get("ANALYTICS_DB_PATH", "./analytics.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    try:
        with _connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    created_at TEXT,
                    query TEXT,
                    query_length INTEGER,
                    level TEXT,
                    section TEXT,
                    semester TEXT,
                    course_type TEXT,
                    num_results INTEGER,
                    used_llm_rerank INTEGER,
                    llm_rerank_failed INTEGER,
                    duration_ms INTEGER
                );

                CREATE INDEX IF NOT EXISTS idx_searches_created_at ON searches(created_at);
                CREATE INDEX IF NOT EXISTS idx_searches_session_id ON searches(session_id);
            """)
    except Exception as e:
        logger.warning("analytics init_db failed: %s", e)


def track_session() -> str:
    if 'analytics_session_id' not in st.session_state:
        session_id = str(uuid.uuid4())
        st.session_state['analytics_session_id'] = session_id
        try:
            with _connect() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO sessions (session_id, created_at) VALUES (?, ?)",
                    (session_id, datetime.now(timezone.utc).isoformat()),
                )
        except Exception as e:
            logger.warning("analytics track_session failed: %s", e)
    return st.session_state['analytics_session_id']


def log_search(
    session_id: str,
    query: str,
    level: str,
    section: str,
    semester: str,
    course_type: str,
    num_results: int,
    used_llm_rerank: bool,
    llm_rerank_failed: bool,
    duration_ms: int,
) -> None:
    try:
        with _connect() as conn:
            conn.execute(
                """INSERT INTO searches
                    (session_id, created_at, query, query_length, level, section, semester,
                     course_type, num_results, used_llm_rerank, llm_rerank_failed, duration_ms)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    datetime.now(timezone.utc).isoformat(),
                    query,
                    len(query),
                    level,
                    section,
                    semester,
                    course_type,
                    num_results,
                    int(used_llm_rerank),
                    int(llm_rerank_failed),
                    duration_ms,
                ),
            )
    except Exception as e:
        logger.warning("analytics log_search failed: %s", e)
