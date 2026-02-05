# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EPFL Course Recommender is a Streamlit application that helps EPFL students find relevant courses by matching job descriptions against the EPFL course catalog. It uses semantic search (sentence embeddings + BM25) and cross-encoder reranking to recommend courses from specific degree programs.

## Architecture

### Data Pipeline (3-stage process)

1. **URL Collection** (`scraper/scraper_urls.py`)
   - Scrapes study plan pages to extract course URLs
   - Filters for coursebook links containing 'fr'
   - Outputs: `data/urls_cours.txt`

2. **Content Extraction** (`scraper/scraper_content.py`)
   - Fetches detailed course information from each URL
   - Extracts: title, content, study plan metadata (level, section, mandatory/optional)
   - Outputs: `data/cours_data_final.json`

3. **Indexing** (`backend/indexer.py`)
   - Generates embeddings using `paraphrase-multilingual-MiniLM-L12-v2`
   - Stores in ChromaDB at `./epfl_cours_db`
   - Collection name: `cours_epfl`
   - Batch processing: 50 courses at a time

### Search Architecture (`app.py`)

The search uses a **hybrid retrieval + reranking** approach:

1. **Candidate Retrieval** (top_k * 2):
   - Dense retrieval: Semantic search via ChromaDB vector similarity
   - Sparse retrieval: BM25 keyword matching
   - Candidates merged via set union

2. **Program Filtering**:
   - Filters candidates by degree program (Bachelor/Master) and section
   - Matches against study plan metadata from scraped data
   - Determines if course is mandatory or optional for the program

3. **Reranking**:
   - CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) scores (query, document) pairs
   - Returns top_k results sorted by reranker score

### Key Data Structures

**Course metadata** (stored in ChromaDB as JSON string):
```python
[
  {
    "level": "Bachelor" | "Master" | "Autre",
    "section": "Informatique" | "Génie civil" | ...,
    "isMandatory": True | False
  }
]
```

**PROGRAMMES dictionary** in app.py:
- Maps UI labels to (section_aliases, level) tuples
- Section aliases handle multilingual variations (e.g., "Informatique", "Computer Science")
- Used for filtering search results by degree program

## Running the Application

### Setup
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install dependencies (if not installed)
pip install streamlit sentence-transformers chromadb rank_bm25
```

### Running the app
```bash
streamlit run app.py
```

### Rebuilding the database

1. Update BASE_URL in `scraper/scraper_urls.py` to target a specific study plan
2. Run the pipeline:
```bash
cd scraper
python scraper_urls.py  # Generates urls_cours.txt
python scraper_content.py  # Generates cours_data_final.json
cd ../backend
python indexer.py  # Rebuilds ChromaDB
```

Note: `backend/indexer.py` paths are relative (`../data/`, `../epfl_cours_db/`), so run from the `backend/` directory.

## Important Implementation Details

### Filtering Logic
- The filtering in `search_courses()` checks if ANY study plan in a course's metadata matches the target program
- Courses can appear in multiple programs (e.g., shared courses across sections)
- "🌐 Tout explorer" bypasses filtering (target_aliases = None)

### Metadata Handling
- Course metadata is stored as JSON string in ChromaDB (limitation: can't store nested dicts directly)
- Must use `json.loads()` when retrieving: `json.loads(meta.get('metadata', '[]'))`

### BM25 Implementation
- BM25 index is built from all documents at startup (cached via `@st.cache_resource`)
- Tokenization: Simple whitespace split (`doc.split()`)
- Search uses same tokenization: `query.split()`

### Score Display
- Reranker scores are unbounded (can be negative)
- UI converts to percentage using sigmoid: `1 / (1 + exp(-(score + 6)))`

## File Organization

```
.
├── app.py                    # Main Streamlit application
├── backend/
│   └── indexer.py           # ChromaDB indexing script
├── scraper/
│   ├── scraper_urls.py      # URL collection
│   ├── scraper_content.py   # Content extraction
│   └── check_data.py        # (utility)
├── data/
│   ├── urls_cours.txt       # Collected course URLs
│   └── cours_data_final.json # Scraped course data
└── epfl_cours_db/           # ChromaDB storage (gitignored)
```

## Models Used

- **Embedder**: `paraphrase-multilingual-MiniLM-L12-v2` (multilingual semantic search)
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (cross-encoder for ranking)
- **BM25**: `rank_bm25.BM25Okapi` (keyword-based retrieval)

All models run on CPU (`device='cpu'`).
