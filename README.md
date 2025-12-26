
# 📄 Policy Question Answering Assistant (RAG)

A **Retrieval-Augmented Generation (RAG)** system.  
The system answers questions about company policy documents using **semantic retrieval + Google Gemini**, with a strong focus on **prompt engineering, hallucination avoidance, and evaluation**.
---
# Live app link : https://rag-policy-system-1.streamlit.app/
---

## 🚀 Features

- Loads real policy documents from disk (`sample_policies/`)
- Cleans and chunks documents (512 characters per chunk)
- Semantic search using Sentence Transformers + ChromaDB
- Answer generation using **Google Gemini (Free Tier)**
- Prompt iteration (baseline vs improved prompt)
- Explicit hallucination control
- Automatic evaluation with results saved to `evaluation_results.json`
- CLI demo + optional Streamlit UI

---

## 🧠 Architecture Overview

```
User Question
      ↓
SentenceTransformer Embedding
      ↓
ChromaDB (Vector Search)
      ↓
Top-k Relevant Chunks
      ↓
Prompt + Context
      ↓
Google Gemini
      ↓
Grounded Answer + Confidence + Sources
```

---

## 📁 Project Structure

```
rag-policy-system/
├── rag_system.py              # Core RAG pipeline + evaluation
├── demo.py                    # CLI demo
├── app.py                     # Streamlit UI (bonus)
├── requirements.txt
├── README.md
├── PROMPT_COMPARISON.md
├── QUICK_REFERENCE.md
├── evaluation_results.json    # Auto-generated
├── .env                       # API key (not committed)
└── sample_policies/
    ├── refund_policy.txt
    ├── shipping_policy.txt
    └── cancellation_policy.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set API key

Create a `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your key from: https://makersuite.google.com/app/apikey

---

## ▶️ Running the Project

### Run evaluation (creates JSON output)
```bash
python rag_system.py
```

### Run CLI demo
```bash
python demo.py
```

### Run Streamlit UI (bonus)
```bash
streamlit run app.py
```

---

## 🧪 Evaluation

- 8 questions tested
- Answerable / Partial / Unanswerable
- Manual rubric: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL
- Results saved automatically to:

```
evaluation_results.json
```

### Design Choice
The system intentionally favors **hallucination avoidance over aggressive confidence**, resulting in some answers marked as *Partial*.  
This trade-off ensures safety and correctness.

---

## 🔁 Prompt Engineering

- **V1**: Basic context injection
- **V2**: Structured prompt with:
  - Explicit grounding rules
  - Confidence scoring
  - Source attribution
  - Clear handling of missing information

See `PROMPT_COMPARISON.md` for details.

---

## 🔮 Future Improvements

- Reranking retrieved chunks
- JSON schema validation
- Multi-document answer synthesis
- Persistent vector store
- Better confidence calibration

---

## ✅ What I’m Most Proud Of

Designing a **safe, grounded RAG system** that avoids hallucinations and clearly communicates uncertainty through evaluation.

## 🔧 What I’d Improve Next

Improve confidence calibration and add reranking to boost answer completeness without sacrificing safety.
