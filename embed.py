"""Embed chunks into ChromaDB and retrieve relevant chunks for a query."""
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

COLLECTION_NAME = "jjay_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DIR = "./chroma_db"


def build_collection(chunks):
    """Embed all chunks and store them in a persistent ChromaDB collection.

    On the first run, embeds all chunks and saves to disk (CHROMA_DIR).
    On subsequent runs, loads the existing collection from disk — no re-embedding.
    To force a rebuild, delete the chroma_db/ directory.

    Args:
        chunks: list of dicts from chunk_documents() — keys: text, source, source_url, chunk_index.

    Returns:
        Tuple of (ChromaDB collection, SentenceTransformer model).
    """
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        if collection.count() == len(chunks):
            print(f"Loaded existing ChromaDB collection ({collection.count()} chunks).\n")
            return collection, model
        # chunk count changed — rebuild
        client.delete_collection(COLLECTION_NAME)

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


REDDIT_SOURCES = [
    "06_reddit_is_jjay_good.txt",
    "07_reddit_first_semester.txt",
    "08_reddit_first_day.txt",
    "09_reddit_graduates.txt",
]

OFFICIAL_SOURCES = [
    "01_student_organizations.txt",
    "02_prism_research.txt",
    "03_honors_programs.txt",
    "04_scholarships.txt",
    "05_quick_facts_2023.txt",
    "10_college_factual_graduation.txt",
    "11_data_usa_jjay.txt",
    "12_career_building.txt",
    "13_federal_work_study.txt",
]


def retrieve(query, collection, model, k=4, source_filter=None):
    """Return the top-k most relevant chunks for a query.

    Args:
        query: question string from the user.
        collection: ChromaDB collection built by build_collection().
        model: SentenceTransformer model used to embed the query.
        k: number of chunks to return (default 4).
        source_filter: optional list of source filenames to restrict results to.
                       Use REDDIT_SOURCES or OFFICIAL_SOURCES, or any custom list.

    Returns:
        List of dicts with keys: text, source, source_url, chunk_index, distance.
    """
    query_embedding = model.encode([query]).tolist()

    where = {"source": {"$in": source_filter}} if source_filter else None
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        where=where,
    )

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

    # metadata filtering demo
    print("=" * 60)
    print("METADATA FILTERING DEMO")
    print("=" * 60)
    filter_query = "What do students think about John Jay College?"

    print(f"\nQuery: {filter_query}")
    print("\n--- No filter (all sources) ---")
    for r in retrieve(filter_query, collection, model, k=4):
        print(f"  [{r['distance']}] ({r['source']}) {r['text'][:100]}")

    print("\n--- Reddit only ---")
    for r in retrieve(filter_query, collection, model, k=4, source_filter=REDDIT_SOURCES):
        print(f"  [{r['distance']}] ({r['source']}) {r['text'][:100]}")

    print("\n--- Official sources only ---")
    for r in retrieve(filter_query, collection, model, k=4, source_filter=OFFICIAL_SOURCES):
        print(f"  [{r['distance']}] ({r['source']}) {r['text'][:100]}")
