
# ⚡ QUICK REFERENCE – Policy RAG System

## Run Everything
```bash
python rag_system.py
```

## CLI Demo
```bash
python demo.py
```

## Streamlit UI
```bash
streamlit run app.py
```

## API Key
Stored in `.env`
```env
GOOGLE_API_KEY=your_key_here
```

## Chunking Strategy
- 512 characters per chunk
- Sentence-based splitting
- Chosen to balance semantic coherence and retrieval precision

## Vector Store
- ChromaDB (in-memory)
- Cosine similarity
- Top-k = 3

## Embeddings
- SentenceTransformer: `all-MiniLM-L6-v2`

## LLM
- Google Gemini `gemini-1.5-flash`
- Free Tier (1,500 requests/day)

## Evaluation Output
- File: `evaluation_results.json`
- Scoring: ✅ / ⚠️ / ❌

## Edge Case Handling
- No relevant docs → “Not mentioned in the policy documents”
- Out-of-scope questions → No hallucination
