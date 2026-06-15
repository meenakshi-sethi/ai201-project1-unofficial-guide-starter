"""End-to-end query function: retrieve relevant chunks and generate a grounded answer."""
from ingest import load_documents, chunk_documents
from embed import build_collection, retrieve
from generate import generate_answer

print("Building index...")
docs = load_documents()
chunks = chunk_documents(docs)
collection, model = build_collection(chunks)
print("Ready.\n")


def ask(question):
    """Run the full RAG pipeline for a question.

    Args:
        question: user question string.

    Returns:
        dict with keys:
            answer (str): grounded LLM response.
            sources (list of str): deduplicated source filenames with URLs.
    """
    retrieved = retrieve(question, collection, model, k=4)
    result = generate_answer(question, retrieved)
    sources = [f"{s['source']}: {s['source_url']}" for s in result["sources"]]
    return {"answer": result["answer"], "sources": sources}
