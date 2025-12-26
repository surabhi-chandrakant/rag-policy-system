import os
import streamlit as st
from rag_system import DocumentProcessor, RAGPipeline

st.set_page_config(
    page_title="Policy Question Answering Assistant",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Policy Question Answering Assistant")
st.caption("RAG system using Google Gemini (100% Free Tier)")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found in .env")
    st.stop()


@st.cache_resource
def load_rag():
    processor = DocumentProcessor()
    rag = RAGPipeline(api_key)

    docs = []
    base = "sample_policies"

    for filename in os.listdir(base):
        path = os.path.join(base, filename)
        text = processor.load(path)
        docs.extend(processor.chunk(text, filename))

    rag.index(docs)
    return rag


rag = load_rag()

query = st.text_input("Ask a question about company policies")

if query:
    with st.spinner("Thinking..."):
        result = rag.ask(query)

    st.subheader("Answer")
    st.write(result["answer"])

    st.markdown(f"**Confidence:** {result['confidence']}")
    st.markdown(
        "**Sources:** " + ", ".join(result["sources"])
        if result["sources"] else "**Sources:** None"
    )
