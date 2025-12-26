import os
import sys
from rag_system import DocumentProcessor, RAGPipeline


def print_result(result):
    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(result["answer"])
    print("-" * 60)
    print(f"Confidence: {result['confidence']}")
    print(f"Sources: {', '.join(result['sources']) if result['sources'] else 'None'}")
    print(f"Documents Retrieved: {result['retrieval']['num_docs_retrieved']}")
    print("=" * 60)


def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not set")
        sys.exit(1)

    processor = DocumentProcessor()
    rag = RAGPipeline(api_key)

    docs = []
    base = "sample_policies"

    for filename in os.listdir(base):
        path = os.path.join(base, filename)
        text = processor.load(path)
        docs.extend(processor.chunk(text, filename))

    rag.index(docs)

    print("\n✓ System ready. Ask questions!\n")

    while True:
        q = input("Your question (type 'exit' to quit): ").strip()
        if q.lower() in ["exit", "quit"]:
            break

        result = rag.ask(q)
        print_result(result)


if __name__ == "__main__":
    main()
