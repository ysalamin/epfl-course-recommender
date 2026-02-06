# 🎓 EPFL Course Recommender

![App preview](demo.png)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.52.2-FF4B4B.svg)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-1.4.0-orange.svg)](https://www.trychroma.com/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4-green.svg)](https://www.crummy.com/software/BeautifulSoup/)
[![NLP](https://img.shields.io/badge/NLP-SentenceTransformers-yellow.svg)](https://www.sbert.net/)

An AI-powered course recommendation system that helps EPFL students discover relevant courses by matching their career interests or job descriptions against the EPFL course catalog using semantic search and intelligent ranking.

## 🚀 Key Features

- **🔍 Semantic Search**: Uses multilingual sentence embeddings (ChromaDB vector database) to understand the *meaning* of queries, not just keywords. Matches course content semantically with job descriptions or interest areas.

- **🎯 Smart Filtering**:
  - Filter by **Academic Level** (Bachelor/Master)
  - Filter by **Section** (Informatique, Génie Civil, Génie Mécanique, etc.)
  - View mandatory vs optional courses for your program

- **⚡ Hybrid Ranking**:
  - **BM25** algorithm for keyword-based retrieval
  - **Vector Similarity** for semantic understanding
  - **Cross-Encoder Reranking** for optimal relevance scoring

- **💼 Pre-built Job Examples**: Jump-start your search with real-world job descriptions across 8+ engineering domains (Data Science, DevOps, Biomedical, Electrical, Mechanical, Civil, Architecture, Materials Science).

- **📊 Transparent Scoring**: See relevance scores for each recommended course to understand why it matches your query.

## 🛠️ Tech Stack

### Core Framework
- **[Streamlit](https://streamlit.io)** - Interactive web application framework

### NLP & Machine Learning
- **[SentenceTransformers](https://www.sbert.net/)** - Multilingual semantic embeddings (`paraphrase-multilingual-MiniLM-L12-v2`)
- **[CrossEncoder](https://www.sbert.net/examples/applications/cross-encoder/README.html)** - Reranking with `ms-marco-MiniLM-L-6-v2`
- **[rank-bm25](https://pypi.org/project/rank-bm25/)** - BM25Okapi keyword matching algorithm

### Data & Storage
- **[ChromaDB](https://www.trychroma.com/)** - Vector database for course embeddings
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** - Web scraping course catalog data
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation

### Supporting Libraries
- **[NumPy](https://numpy.org/)** & **[SciPy](https://scipy.org/)** - Numerical computing
- **[PyTorch](https://pytorch.org/)** - Deep learning backend
- **[scikit-learn](https://scikit-learn.org/)** - Machine learning utilities

## ⚙️ Installation & Usage

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd epfl-recommender
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`

### 🔄 Rebuilding the Database (Optional)

If you want to update the course catalog or rebuild the vector database:

1. **Collect course URLs**
   ```bash
   cd scraper
   python scraper_urls.py
   ```

2. **Scrape course content**
   ```bash
   python scraper_content.py
   ```

3. **Rebuild ChromaDB index**
   ```bash
   cd ../backend
   python indexer.py
   ```

## 📂 Project Structure

```
epfl-recommender/
├── app.py                      # Main Streamlit application
├── backend/
│   └── indexer.py             # ChromaDB indexing pipeline
├── scraper/
│   ├── scraper_urls.py        # Course URL collector
│   ├── scraper_content.py     # Course content extractor
│   └── check_data.py          # Data validation utility
├── data/
│   ├── urls_cours.txt         # Collected course URLs
│   └── cours_data_final.json  # Scraped course metadata
├── epfl_cours_db/             # ChromaDB vector storage (generated)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎯 How It Works

### Search Pipeline

1. **Query Input**: User enters a job description or describes their interests
2. **Candidate Retrieval**:
   - Dense retrieval via semantic vector search
   - Sparse retrieval via BM25 keyword matching
   - Union of candidates for comprehensive coverage
3. **Program Filtering**: Filter courses by selected degree program and section
4. **Reranking**: CrossEncoder scores all candidates and returns top results
5. **Display**: Results shown with relevance scores and program metadata

### Models Used

- **Embedder**: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim vectors)
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Retriever**: BM25Okapi with custom tokenization

All models run on CPU for broad compatibility.

## 🔮 Future Improvements

- [ ] **User Profiles**: Save preferences and track course recommendations over time
- [ ] **Enhanced Metadata**: Include professor ratings, course difficulty, workload estimates
- [ ] **Semester Planning**: Multi-semester course planning with prerequisite tracking
- [ ] **Collaborative Filtering**: Recommend courses based on similar student profiles
- [ ] **Course Reviews**: Integrate student feedback and ratings
- [ ] **Export Functionality**: Export recommended courses to PDF/CSV
- [ ] **Multi-language Support**: Full UI localization (French, German, Italian)
- [ ] **Real-time Updates**: Automated scraping for up-to-date course information

## 📄 License

This project is intended for educational purposes at EPFL.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

Built with ❤️ for EPFL students
