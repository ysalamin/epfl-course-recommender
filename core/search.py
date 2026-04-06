import math
import streamlit as st
import anthropic
import numpy as np
import json
import logging

from core.utils import TOP_K_RETRIEVAL

logger = logging.getLogger(__name__)


def expand_query(query):
    """
    Use Claude to expand a query with relevant technical terms.
    Returns a comma-separated string of terms in English and French.
    Falls back to an empty string on any error.
    """
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            system=(
                "You are a technical vocabulary expander for academic course search. "
                "Given a job title or description, extract key technical skills and academic topics. "
                "Return ONLY a comma-separated list of relevant terms in both English and French. "
                "No explanation, no preamble, no bullet points — just the terms."
            ),
            messages=[{"role": "user", "content": query}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.warning("Query expansion failed, falling back to original query: %s", e)
        return ""


@st.cache_data(ttl=3600)
def llm_rerank(query: str, candidate_tuples: tuple) -> dict | None:
    """
    Use Claude to rerank candidates by relevance to the query.

    Args:
        query: The job description / search query.
        candidate_tuples: Tuple of (course_id, title, content_preview) — hashable for caching.

    Returns:
        Dict mapping course_id -> {'score': int (0-100), 'reason': str}, or None on failure.
    """
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

        courses_text = "\n".join(
            f"{i+1}. Title: {title}\n   Preview: {preview}"
            for i, (cid, title, preview) in enumerate(candidate_tuples)
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=(
                "You are a course recommendation engine for EPFL students. "
                "Given a job description or interest description and a list of courses, rank them by relevance. "
                "Return ONLY a JSON array of objects with three fields: 'title', 'score' (0-100), and 'reason' "
                "(a 1-2 sentence explanation in French of why this course is relevant or not to the query). "
                "Example: {\"title\": \"Probabilités et statistique\", \"score\": 92, \"reason\": \"Ce cours couvre les fondamentaux de probabilités et statistiques, essentiels pour la modélisation quantitative et l'analyse de risques.\"} "
                "Sort by score descending. No preamble, no markdown — just the JSON array. "
                "Consider that foundational courses (electronics, mathematics, physics) are highly relevant "
                "to applied engineering fields, even if their description doesn't explicitly mention the application domain."
            ),
            messages=[{
                "role": "user",
                "content": f"Job description:\n{query}\n\nCourses:\n{courses_text}"
            }],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        logger.debug("LLM rerank raw response: %.200s", raw)

        ranked = json.loads(raw)
        title_to_item = {item['title']: item for item in ranked}

        result = {}
        for cid, title, _ in candidate_tuples:
            item = title_to_item.get(title)
            if item is None:
                for t, it in title_to_item.items():
                    if title.lower() in t.lower() or t.lower() in title.lower():
                        item = it
                        break
            if item is not None:
                result[cid] = {'score': item.get('score', 0), 'reason': item.get('reason', '')}
            else:
                result[cid] = {'score': 0, 'reason': ''}

        return result

    except Exception as e:
        logger.warning("LLM rerank failed, falling back to combined scoring: %s", e)
        return None


def search_courses(query, filters, embedder, collection, bm25, all_data):
    """
    Hybrid retrieval pipeline:
    1. Metadata filtering  — narrow to courses matching level/section/semester/type
    2. If query provided:
       a. BM25 retrieval    — keyword scoring on filtered subset, take top-K
       b. Semantic retrieval — cosine similarity on embeddings, take top-K
       c. Merge             — union of both top-K sets
       d. Combined score    — 0.7*cosine_norm + 0.3*bm25_norm (used as fallback)
       e. LLM reranking     — Claude assigns 0-100 relevance scores (rate-limited to 20/session)
    3. If no query: return all filtered courses alphabetically
    """
    target_level, target_section, semester_filter, course_type_filter = filters

    logger.debug(
        "Search — level=%s, section=%s, semester=%s, type=%s",
        target_level, target_section, semester_filter, course_type_filter
    )

    # Step 1: Filter by metadata
    filtered_candidates = []
    for idx, cid in enumerate(all_data['ids']):
        meta = all_data['metadatas'][idx]
        plans = json.loads(meta.get('metadata', '[]'))

        for plan in plans:
            lvl = plan.get('level', '')
            sec = plan.get('section', '').strip()
            course_type = plan.get('type', '')
            sem = plan.get('semester', '')

            level_match = (lvl == target_level)
            section_match = (sec == target_section)
            type_match = True if course_type_filter == "Tous" else (course_type == course_type_filter)
            semester_match = (sem == semester_filter)

            if level_match and section_match and type_match and semester_match:
                logger.debug("Match: %s | %s | %s | %s | %s", meta.get('title', 'N/A')[:50], lvl, sec, course_type, sem)
                filtered_candidates.append({
                    "id": cid,
                    "content": all_data['documents'][idx],
                    "meta": meta,
                    "level": lvl,
                    "section": sec,
                    "type": course_type,
                    "semester": sem
                })
                break

    # Deduplicate by title
    seen_titles = set()
    unique_candidates = []
    for candidate in filtered_candidates:
        title = candidate['meta']['title']
        if title not in seen_titles:
            unique_candidates.append(candidate)
            seen_titles.add(title)
    filtered_candidates = unique_candidates

    logger.debug("Courses after filtering: %d", len(filtered_candidates))

    if not filtered_candidates:
        return []

    # Step 2: No query — return alphabetically
    if not query or not query.strip():
        filtered_candidates.sort(key=lambda x: x['meta']['title'])
        for candidate in filtered_candidates:
            candidate['score'] = 0
        return filtered_candidates

    # Step 3: Hybrid retrieval — BM25 + Semantic

    expanded_terms = expand_query(query)
    enriched_query = f"{query} {expanded_terms}" if expanded_terms else query
    logger.debug("Query expansion: %r → %r", query, expanded_terms)

    id_to_global_idx = {cid: idx for idx, cid in enumerate(all_data['ids'])}

    # BM25 retrieval
    all_bm25_scores = bm25.get_scores(enriched_query.split())
    bm25_scored = [
        (candidate, float(all_bm25_scores[id_to_global_idx[candidate['id']]]) if id_to_global_idx.get(candidate['id']) is not None else 0.0)
        for candidate in filtered_candidates
    ]
    bm25_scored.sort(key=lambda x: x[1], reverse=True)
    bm25_top = bm25_scored[:TOP_K_RETRIEVAL]
    bm25_top_ids = {c['id'] for c, _ in bm25_top}

    logger.debug("BM25 top-%d: %s", TOP_K_RETRIEVAL, [(c['meta']['title'][:30], f"{s:.4f}") for c, s in bm25_top])

    # Semantic retrieval
    query_embedding = embedder.encode(enriched_query)
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)

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

    logger.debug("Semantic top-%d: %s", TOP_K_RETRIEVAL, [(c['meta']['title'][:30], f"{s:.4f}") for c, s in semantic_top])

    # Merge
    merged_ids = bm25_top_ids | semantic_top_ids
    merged_candidates = [c for c in filtered_candidates if c['id'] in merged_ids]

    logger.debug("Merged candidates: %d (BM25=%d, Semantic=%d, overlap=%d)",
                 len(merged_candidates), len(bm25_top_ids), len(semantic_top_ids),
                 len(bm25_top_ids & semantic_top_ids))

    # Combined scoring (fallback)
    id_to_cosine = {c['id']: s for c, s in semantic_scored}
    id_to_bm25 = {c['id']: s for c, s in bm25_scored}

    raw_cosines = [id_to_cosine.get(c['id'], 0.0) for c in merged_candidates]
    raw_bm25s   = [id_to_bm25.get(c['id'],   0.0) for c in merged_candidates]

    def minmax_norm(vals):
        lo, hi = min(vals), max(vals)
        return [((v - lo) / (hi - lo)) if hi > lo else 0.5 for v in vals]

    cosine_norm = minmax_norm(raw_cosines)
    bm25_norm   = minmax_norm(raw_bm25s)

    id_to_combined = {}
    for candidate, cn, bn in zip(merged_candidates, cosine_norm, bm25_norm):
        combined = 0.7 * cn + 0.3 * bn
        candidate['score'] = combined
        id_to_combined[candidate['id']] = combined

    logger.debug("Combined score stats — min=%.4f max=%.4f mean=%.4f",
                 min(id_to_combined.values()), max(id_to_combined.values()),
                 sum(id_to_combined.values()) / len(id_to_combined))

    # LLM Reranking
    llm_search_count = st.session_state.get('llm_search_count', 0)
    use_llm = llm_search_count < 20

    llm_scores = None
    if use_llm:
        candidate_tuples = tuple(
            (c['id'], c['meta']['title'], c['content'][:300])
            for c in merged_candidates
        )
        llm_scores = llm_rerank(query, candidate_tuples)
    else:
        st.warning("⚠️ Limite de 20 recherches LLM par session atteinte. Utilisation du scoring BM25/sémantique.")
        logger.info("LLM rerank rate limit reached (%d/20).", llm_search_count)

    if llm_scores is not None:
        st.session_state['llm_search_count'] = llm_search_count + 1

        for candidate in merged_candidates:
            llm_entry = llm_scores.get(candidate['id'], {'score': 0, 'reason': ''})
            candidate['llm_score'] = llm_entry['score']
            candidate['llm_reason'] = llm_entry['reason']

        merged_candidates.sort(key=lambda x: x.get('llm_score', 0), reverse=True)

        logger.debug("LLM reranking vs combined: %s",
                     [(c['meta']['title'][:30], c.get('llm_score', 0), f"{id_to_combined[c['id']]:.4f}")
                      for c in merged_candidates])

        for candidate in merged_candidates:
            candidate['display_score'] = candidate.get('llm_score', 0) / 100.0

    else:
        if use_llm:
            logger.warning("LLM rerank returned None, falling back to combined scoring.")

        merged_candidates.sort(key=lambda x: x['score'], reverse=True)

        for candidate in merged_candidates:
            # sigmoid centered at 0.5 with k=4, maps [0,1] → [~0.12, ~0.88]
            candidate['display_score'] = 1.0 / (1.0 + math.exp(-4.0 * (candidate['score'] - 0.5)))

    logger.debug("Final ranking: %s",
                 [(i+1, c['meta']['title'][:30], f"{c['display_score']*100:.1f}%")
                  for i, c in enumerate(merged_candidates)])

    return merged_candidates
