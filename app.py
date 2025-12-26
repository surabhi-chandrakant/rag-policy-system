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
    st.error("GOOGLE_API_KEY not found in Streamlit Secrets")
    st.stop()


@st.cache_resource
def load_rag():
    processor = DocumentProcessor()
    rag = RAGPipeline(api_key)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    POLICY_DIR = os.path.join(BASE_DIR, "sample_policies")

    if not os.path.exists(POLICY_DIR):
        st.error("sample_policies folder not found in repo")
        st.stop()

    docs = []
    for filename in os.listdir(POLICY_DIR):
        path = os.path.join(POLICY_DIR, filename)
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
