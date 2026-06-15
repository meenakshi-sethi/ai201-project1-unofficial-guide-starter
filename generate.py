"""Generate a grounded answer using Groq LLM and retrieved chunks."""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful guide for students at John Jay College of Criminal Justice (CUNY).

Answer the question using ONLY the information provided in the context below.
Do not use any outside knowledge or make anything up.
If the context does not contain enough information to answer the question, respond with exactly:
"I don't have enough information in my sources to answer that question."

Keep your answer clear and concise. Use plain language."""


def generate_answer(query, chunks):
    """Generate a grounded answer from retrieved chunks using Groq.

    Args:
        query: user question string.
        chunks: list of dicts from retrieve() — keys: text, source, source_url, distance.

    Returns:
        dict with keys:
            answer (str): the LLM response.
            sources (list of dicts): deduplicated list of {source, source_url}.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] (from {chunk['source']})\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
    )

    answer = response.choices[0].message.content

    seen = set()
    sources = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.add(chunk["source"])
            sources.append({"source": chunk["source"], "source_url": chunk["source_url"]})

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    from ingest import load_documents, chunk_documents
    from embed import build_collection, retrieve

    docs = load_documents()
    chunks = chunk_documents(docs)
    collection, model = build_collection(chunks)

    test_queries = [
        "What is the PRISM program at John Jay?",
        "What do Reddit users say about transferring to John Jay?",
        "What is the weather like on Mars?",  # out-of-scope
    ]

    for query in test_queries:
        print(f"Q: {query}")
        retrieved = retrieve(query, collection, model, k=4)
        result = generate_answer(query, retrieved)
        print(f"A: {result['answer']}")
        print("Sources:")
        for s in result["sources"]:
            print(f"  - {s['source']}: {s['source_url']}")
        print()
