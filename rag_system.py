"""
RAG System for Policy Documents – Google Gemini
Creates evaluation_results.json
"""

import os
import re
import json
from typing import List, Dict
from dataclasses import dataclass

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


# =====================
# Data Structures
# =====================

@dataclass
class Document:
    content: str
    metadata: Dict
    doc_id: str


# =====================
# Document Processor
# =====================

class DocumentProcessor:
    def __init__(self, chunk_size: int = 512):
        self.chunk_size = chunk_size

    def load(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def clean(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def chunk(self, text: str, source: str) -> List[Document]:
        text = self.clean(text)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks, current, idx = [], "", 0
        for s in sentences:
            if len(current) + len(s) <= self.chunk_size:
                current += s + " "
            else:
                chunks.append(Document(
                    content=current.strip(),
                    metadata={"source": source},
                    doc_id=f"{source}_{idx}"
                ))
                idx += 1
                current = s + " "

        if current:
            chunks.append(Document(
                content=current.strip(),
                metadata={"source": source},
                doc_id=f"{source}_{idx}"
            ))

        return chunks


# =====================
# RAG Pipeline
# =====================

class RAGPipeline:
    def __init__(self, api_key: str):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        self.client = chromadb.Client(
            Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.create_collection(
            name="policy_docs",
            metadata={"hnsw:space": "cosine"}
        )

        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel("gemini-1.5-flash")

        self.store: Dict[str, Document] = {}

    def index(self, docs: List[Document]):
        texts = [d.content for d in docs]
        embeddings = self.embedder.encode(texts)

        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[d.metadata for d in docs],
            ids=[d.doc_id for d in docs]
        )

        for d in docs:
            self.store[d.doc_id] = d

    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        q_emb = self.embedder.encode([query])
        res = self.collection.query(
            query_embeddings=q_emb.tolist(),
            n_results=k
        )

        docs = []
        if res["ids"] and res["ids"][0]:
            for did in res["ids"][0]:
                docs.append(self.store[did])

        return docs

    def answer(self, query: str, docs: List[Document]) -> Dict:
        if not docs:
            return {
                "answer": "Not mentioned in the policy documents.",
                "confidence": "none",
                "sources": []
            }

        top = docs[0]

        prompt = f"""
Answer ONLY using the policy text below.
If the answer is not present, say: Not mentioned in the policy documents.

Policy Text:
{top.content}

Question:
{query}
"""

        try:
            resp = self.llm.generate_content(prompt)
            text = (resp.text or "").strip()
            if text:
                return {
                    "answer": text,
                    "confidence": "medium",
                    "sources": [top.metadata["source"]]
                }
        except Exception:
            pass

        return {
            "answer": top.content,
            "confidence": "low",
            "sources": [top.metadata["source"]]
        }

    def ask(self, query: str) -> Dict:
        docs = self.retrieve(query)
        result = self.answer(query, docs)
        result["retrieval"] = {"num_docs_retrieved": len(docs)}
        return result


# =====================
# Evaluation
# =====================

def run_evaluation(rag: RAGPipeline):
    test_cases = [
        ("What is your refund policy?", "answerable"),
        ("How long do I have to return a product?", "answerable"),
        ("Can I cancel after shipping?", "answerable"),
        ("Do you offer free returns?", "partial"),
        ("What are international shipping costs?", "partial"),
        ("What is your privacy policy?", "unanswerable"),
        ("Do you sell laptops?", "unanswerable"),
        ("What are your office hours?", "unanswerable"),
    ]

    results = []

    for q, expected in test_cases:
        res = rag.ask(q)

        if expected == "unanswerable":
            score = "✅ PASS" if res["confidence"] in ["none", "low"] else "❌ FAIL"
        else:
            score = "⚠️ PARTIAL" if res["confidence"] == "low" else "✅ PASS"

        results.append({
            "question": q,
            "expected": expected,
            "answer": res["answer"],
            "confidence": res["confidence"],
            "sources": res["sources"],
            "score": score
        })

    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {"total": len(results), "results": results},
            f,
            indent=2
        )

    print("✓ evaluation_results.json created")


# =====================
# Main
# =====================

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY missing")
        return

    processor = DocumentProcessor()
    rag = RAGPipeline(api_key)

    docs = []
    base = "sample_policies"

    for filename in os.listdir(base):
        path = os.path.join(base, filename)
        text = processor.load(path)
        docs.extend(processor.chunk(text, filename))

    rag.index(docs)
    run_evaluation(rag)


if __name__ == "__main__":
    main()
