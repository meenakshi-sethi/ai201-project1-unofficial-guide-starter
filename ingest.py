"""Document pipeline: load, clean, and chunk all source documents."""
import os
import re

DOCS_DIR = "documents"


def load_documents(docs_dir=DOCS_DIR):
    """Load all .txt files from docs_dir.

    Args:
        docs_dir: path to the folder containing source .txt files.

    Returns:
        List of dicts with keys 'filename' (str) and 'text' (str).
    """
    documents = []
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"filename": filename, "text": text})
    return documents


def clean_text(text):
    """Remove boilerplate and noise from a document's raw text.

    Strips nav chrome, Reddit UI elements, vote counts, timestamps,
    subreddit header lines, Reddit usernames, and promoted ad content.
    Collapses multiple blank lines. SOURCE line is handled separately
    in chunk_documents and should not be passed in here.

    Args:
        text: raw document text with SOURCE line already removed.

    Returns:
        Cleaned string with noise removed.
    """
    lines = text.splitlines()
    cleaned = []
    skip_ad_lines = 0
    for line in lines:
        stripped = line.strip()

        # skip ad body/CTA lines that follow a "Promoted" marker (2 lines per ad block)
        if skip_ad_lines > 0:
            skip_ad_lines -= 1
            continue

        # skip known boilerplate phrases
        if stripped in (
            "Skip to main content",
            "r/CUNY Search in r/CUNY Create",
            "Join the conversation",
            "Sort by: Best Search Comments",
            "Share",
            "Reply",
            "More",
            "Image",
        ):
            continue

        # skip Reddit promoted ad lines and queue next 2 lines as ad body/CTA
        if "Promoted" in stripped:
            skip_ad_lines = 2
            continue

        # skip ad CTA lines that slip past the counter (e.g. "Download databricks.com")
        if re.fullmatch(r"(Download|Shop Now|Sign Up|Get Started|Learn More)\s+\S+\.\S+", stripped):
            continue

        # skip Reddit vote count lines (e.g. "82 19", "26 25")
        if re.fullmatch(r"\d+\s+\d+", stripped):
            continue

        # skip standalone timestamp lines (e.g. "2y ago", "6y ago", "3mo ago")
        if re.fullmatch(r"\d+[ymd]o?\s+ago", stripped):
            continue

        # skip Reddit subreddit + timestamp header lines (e.g. "r/CUNY •2y ago")
        if re.match(r"r/\w+\s*[•·]\s*\d+", stripped):
            continue

        # skip Reddit username lines (standalone word with underscores/digits, no spaces)
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{4,29}", stripped) and "_" in stripped:
            continue

        # skip page title lines with site name suffix
        if "| John Jay College of Criminal Justice" in line:
            continue

        cleaned.append(line)

    # collapse multiple blank lines into one
    result = "\n".join(cleaned)
    result = re.sub(r"\n{3,}", "\n\n", result)
    # remove PDF bullet characters and HTML encoding artifacts
    result = result.replace("■", "").replace("Â", "")
    return result.strip()


def _recursive_split(text, separators, chunk_size, overlap):
    """Internal recursive helper — splits text using the first matching separator.

    Args:
        text: text to split.
        separators: list of separators to try in order (coarsest to finest).
        chunk_size: max characters per chunk.
        overlap: characters to carry over from the previous chunk.

    Returns:
        List of string chunks.
    """
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    sep_idx = None
    for i, s in enumerate(separators):
        if s in text:
            sep_idx = i
            break

    if sep_idx is None:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end].strip())
            if end >= len(text):
                break
            start = end - overlap
        return [c for c in chunks if c]

    sep = separators[sep_idx]
    next_seps = separators[sep_idx + 1:]
    parts = [p.strip() for p in text.split(sep) if p.strip()]

    chunks = []
    current = ""

    for part in parts:
        candidate = (current + sep + part).strip() if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
                # snap overlap to nearest word boundary so chunks never start mid-word
                if overlap:
                    start = len(current) - overlap
                    space_idx = current.find(" ", start)
                    overlap_text = current[space_idx:].strip() if space_idx != -1 else current[start:].strip()
                else:
                    overlap_text = ""
                candidate_with_overlap = (overlap_text + " " + part).strip() if overlap_text else part
                if len(candidate_with_overlap) <= chunk_size:
                    current = candidate_with_overlap
                else:
                    # overlap + part already exceeds limit; split part and start fresh
                    sub = _recursive_split(part, next_seps, chunk_size, overlap)
                    chunks.extend(sub)
                    current = ""
            else:
                sub = _recursive_split(part, next_seps, chunk_size, overlap) if next_seps else [part]
                chunks.extend(sub)
                current = ""

    if current.strip():
        if len(current.strip()) > chunk_size:
            chunks.extend(_recursive_split(current.strip(), next_seps, chunk_size, overlap))
        else:
            chunks.append(current.strip())

    return [c for c in chunks if c.strip()]


def chunk_text(text, chunk_size=300, overlap=50):
    """Split a cleaned document into chunks using recursive character splitting.

    Tries separators in order: paragraph break → newline → sentence → word.
    Falls back to a hard cut only when no separator fits.

    Args:
        text: cleaned document text.
        chunk_size: max characters per chunk (default 300).
        overlap: characters carried over from the previous chunk (default 50).

    Returns:
        List of string chunks.
    """
    separators = ["\n\n", "\n", ". ", " "]
    return _recursive_split(text.strip(), separators, chunk_size, overlap)


def chunk_documents(documents, chunk_size=300, overlap=50):
    """Clean and chunk all documents, attaching source metadata to each chunk.

    Extracts the SOURCE URL from each document before cleaning so the long
    URL never reaches the chunker and bleeds across chunk boundaries.
    Filters out chunks shorter than 30 chars to remove leftover fragments.

    Args:
        documents: list of dicts with 'filename' and 'text' keys (from load_documents).
        chunk_size: max characters per chunk (default 300).
        overlap: overlap between consecutive chunks (default 50).

    Returns:
        List of dicts with keys: 'text', 'source', 'source_url', 'chunk_index'.
    """
    all_chunks = []
    for doc in documents:
        # fix 1: extract SOURCE url before cleaning so it never enters the chunker
        lines = doc["text"].splitlines()
        source_url = ""
        if lines and lines[0].startswith("SOURCE:"):
            source_url = lines[0].replace("SOURCE:", "").strip()
            body = "\n".join(lines[1:])
        else:
            body = doc["text"]

        cleaned = clean_text(body)
        chunks = chunk_text(cleaned, chunk_size, overlap)

        for i, chunk in enumerate(chunks):
            # fix 3: skip very short fragments (under 30 chars)
            if len(chunk.strip()) < 30:
                continue
            all_chunks.append({
                "text": chunk,
                "source": doc["filename"],
                "source_url": source_url,
                "chunk_index": i,
            })
    return all_chunks


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents\n")

    # Stage 2: verify cleaning — before/after for one web doc and one Reddit doc
    for filename in ["01_student_organizations.txt", "06_reddit_is_jjay_good.txt"]:
        doc = next(d for d in docs if d["filename"] == filename)
        cleaned = clean_text(doc["text"])
        print(f"=== BEFORE: {filename} (first 300 chars) ===")
        print(doc["text"][:300])
        print(f"\n=== AFTER: {filename} (first 300 chars) ===")
        print(cleaned[:300])
        print()

    # Stage 3: chunk all documents and inspect
    chunks = chunk_documents(docs)
    print(f"Total chunks: {len(chunks)}\n")

    import random
    random.seed(42)
    samples = random.sample(chunks, min(5, len(chunks)))
    for i, chunk in enumerate(samples, 1):
        print(f"--- Sample {i} | {chunk['source']} | chunk #{chunk['chunk_index']} ---")
        print(chunk["text"])
        print()

