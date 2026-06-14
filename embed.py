"""Embed chunks into ChromaDB and retrieve relevant chunks for a query."""
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

COLLECTION_NAME = "jjay_guide"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_collection(chunks):
    """Embed all chunks and store them in a ChromaDB collection.

    Clears any existing collection with the same name before loading,
    so re-running always produces a fresh index.

    Args:
        chunks: list of dicts from chunk_documents() — keys: text, source, source_url, chunk_index.

    Returns:
        The ChromaDB collection.
    """
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.Client()

    # drop and recreate so re-runs don't duplicate
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    ids = [f"{c['source']}__chunk{c['chunk_index']}" for c in chunks]
    metadatas = [
        {"source": c["source"], "source_url": c["source_url"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    print(f"Embedding {len(texts)} chunks with {MODEL_NAME}...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)
    print(f"Stored {collection.count()} chunks in ChromaDB.\n")
    return collection, model


def retrieve(query, collection, model, k=4):
    """Return the top-k most relevant chunks for a query.

    Args:
        query: question string from the user.
        collection: ChromaDB collection built by build_collection().
        model: SentenceTransformer model used to embed the query.
        k: number of chunks to return (default 4).

    Returns:
        List of dicts with keys: text, source, source_url, chunk_index, distance.
    """
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "source_url": results["metadatas"][0][i]["source_url"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": round(results["distances"][0][i], 4),
        })
    return chunks


if __name__ == "__main__":
    # build the index
    docs = load_documents()
    chunks = chunk_documents(docs)
    collection, model = build_collection(chunks)

    # test with all 5 evaluation questions from planning.md
    test_queries = [
        "What is the total student enrollment at John Jay College as of Fall 2023?",
        "What is the 6-year graduation rate at John Jay?",
        "Who is eligible for the Federal Work-Study program at John Jay?",
        "What is the PRISM program at John Jay?",
        "What do Reddit users say about transferring to John Jay?",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        results = retrieve(query, collection, model, k=4)
        for r in results:
            print(f"  [{r['distance']}] ({r['source']}) {r['text'][:120]}")
        print()
