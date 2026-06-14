# Project Decisions Log

## Chunking Strategy

**Recursive character splitting, chunk size 300, overlap 50**

**How I decided:**
After skimming all 13 documents, most content is short and structured — club descriptions (~150-200 chars), program summaries (~200-300 chars), FAQ pairs (~250-350 chars), Reddit comments (~150-300 chars). Only document 08 (Reddit first day) has longer paragraphs.

Two options I considered:

- **Hybrid fixed-size with overlap** — splits at a fixed character count regardless of content. Simple and predictable, but risks cutting mid-sentence or splitting a Q&A pair across two chunks. For this corpus where each entry carries its own meaning, a bad split loses context entirely.

- **Recursive character splitting** — tries to split at natural boundaries in order: paragraph break → sentence → word. Only falls back to a hard cut if nothing else fits. This is the production standard for mixed/messy content because it adapts to the document rather than forcing a fixed grid onto it.

I chose recursive because the corpus is mixed — some documents are dense stats, some are FAQ pairs, some are Reddit threads. A fixed split would handle none of these well. Recursive handles all of them without special-casing each document type.

Chunk size 300 keeps each entry as its own chunk. Overlap of 50 (up from an initial 30) adds a small safety net for sentences that straddle a boundary, especially in the longer Reddit comments.

---

## Retrieval Approach

**Embedding model: `all-MiniLM-L6-v2`**
Runs locally, no API key, no rate limits. The corpus is small and content is general — no need for a large domain-specific model. Its 256-token context window fits the 300-char chunks without truncation. Alternatives like `text-embedding-3-large` would improve accuracy but add API cost and latency not justified for this project size.

**Top-k: 3**
Entries are short and self-contained. 3 chunks gives enough context (~900 chars) for most questions. Going higher risks pulling in off-topic chunks given how small the dataset is. Risk noted: broad opinion questions may need more Reddit chunks than 3 — will verify during evaluation in Milestone 4.

**Why semantic embedding works well for Reddit content**
Reddit comments use informal conversational language. Semantic embeddings handle this well since the model encodes meaning rather than matching exact words. A query like "is John Jay worth going to" will find relevant Reddit chunks even when comments don't use those exact words.

**Anticipated retrieval risks**
- Chunk size 300 is too large relative to thin documents (Career Building ~1,500 chars, Quick Facts ~1,700 chars) — only 4-5 chunks each, limited retrieval options
- Broad queries fail with top-k 3 — answers needing multiple entries will be incomplete
- Same stat in multiple sources (graduation rate differs across Quick Facts, Data USA, College Factual) — LLM may get conflicting context
- Reddit PDF noise (vote counts, timestamps, UI elements) mixed into extracted text may hurt embedding quality

---

## Milestone 3 — Overlap Word Boundary Fix

**Overlap snaps to nearest word boundary instead of hard character cut**
Initial implementation used `current[-overlap:]` which cut at exactly 50 chars and could land mid-word, making chunk starts like `mployer...` or `nitieis...`. Fixed by finding the first space after position `len(current) - overlap` and starting the overlap from there. Overlap becomes slightly variable (~45–55 chars) but every chunk starts at a clean word.

This is standard in production RAG — LangChain's `RecursiveCharacterTextSplitter` does the same. Matters for source citations (mid-word starts look broken to users), BM25 hybrid search (partial tokens hurt keyword matching), and marginal embedding quality improvement.

**Before and after chunk count:**
- Before fix: 690 chunks — SOURCE URL was eating into chunk space, and hard character overlap occasionally created extra chunk boundaries
- After fix: 674 chunks — 16 fewer chunks because snapping to the next word boundary makes each overlap slightly shorter, so each chunk absorbs a bit more content per boundary
- Both counts are within the required 50–2,000 range

---

## Milestone 3 — Oversized Chunks Bug (Stage 3)

**Bug: 101 chunks exceeded 300 chars (max was 1,132)**

Two causes found and fixed:

**Cause 1 — overlap + large part exceeded chunk_size silently**
When saving a chunk and computing the new `current = overlap_text (~50 chars) + part (~270 chars)`, the combination was already > 300 chars. The loop just accepted it as `current`, and then the next iteration appended this oversized `current` as a chunk. Fix: check `len(overlap + part)` before setting it as `current`. If it's already over the limit, recursively split `part` and reset `current` to empty.

**Cause 2 — end-of-loop current not re-split**
If the loop ended with `current` still oversized (e.g. set by cause 1 before the fix), the final `if current: chunks.append(current)` appended it as-is. Fix: check `len(current) > chunk_size` before appending; if so, recursively split it first.

**Before and after chunk count:**
- Before fix: 674 chunks, 101 over 300 chars, max 1,132 chars
- After fix: 767 chunks, 0 over 300 chars, max exactly 300 chars
- Chunk count increased by 93 because the previously oversized chunks are now correctly split into smaller ones
- All 767 chunks are within the required 50–2,000 range

---

## Milestone 3 — Issues Found During Chunk Inspection (Stage 3)

After running the full pipeline and inspecting 5 sample chunks, three critical issues were found that must be fixed before embedding (per project instructions: "bad chunks cannot be fixed by tuning retrieval later"):

**Issue 1 — URL tail bleeding into chunks**
The SOURCE line at the top of each file contains a long URL. When the chunker hits the 300-char boundary mid-URL, the tail of the URL (e.g. `egraduate-researchcreativity-assistant-scholarship`) becomes the start of the next chunk. That chunk is an unreadable fragment. Fix: strip the SOURCE URL out of the chunk text before splitting and store it only in metadata.

**Issue 2 — Promoted ad content slipping through**
Reddit PDFs include sponsored ads (e.g. `Intuit_QuickBooks • Promoted Get 50% off QuickBooks for 3 months`). The cleaning step didn't target these. Instructions explicitly say "Remove: ads." Fix: detect and strip lines containing `• Promoted` or `Promoted` as a standalone marker.

**Issue 3 — Short boilerplate fragments surviving as chunks**
Lines like `9 Reply`, `CONGRATSSS`, and similar reaction text from Reddit survived cleaning and became standalone chunks. Instructions say "Remove: share buttons, comment counts." These produce chunks with no standalone meaning. Fix: filter out chunks shorter than a minimum length (e.g. 30 chars) after splitting.

**Issue 4 — "Image" artifacts from scraped pages**
Web pages contain `<img>` tags with `alt="Image"`. BeautifulSoup's `get_text()` extracts the alt text as a standalone line `"Image"` in the document. This shows up as a meaningless 5-char chunk or gets concatenated with the next real line. Fix: added `"Image"` to the boilerplate skip list in `clean_text`.

---

## Milestone 3 — Issues Found During Loading (Stage 1)

After running the loader and inspecting the first 200 chars of each document, these cleaning problems were identified:

**All web-scraped files (01–04, 10, 12, 13):**
- `Skip to main content` — navigation boilerplate at the top of every page
- Page title repeated as a header (e.g. `John Jay College of Criminal Justice`)

**Reddit files (06–09):**
- `Skip to main content` — same nav boilerplate
- `r/CUNY Search in r/CUNY Create` — Reddit UI chrome printed into the PDF
- Vote counts as bare numbers (e.g. `82 19`, `26 25`) — upvote/downvote extracted as text
- Timestamps (e.g. `2y ago`, `6y ago`) mixed into comment text
- Usernames appearing as standalone lines

**All files:**
- `SOURCE: <url>` line at the top — useful for attribution, must be preserved not stripped

These all need to be removed in the cleaning step before chunking.

---

## Document Collection

**Single collection script (`collect_documents.py`)**
One file handles all document collection. Helper functions (fetch_text, fetch_pdf, extract_pdf_to_txt) live at the top; collection logic runs under `if __name__ == "__main__"`. Avoids splitting across utilities.py + separate scripts.

**Mixed collection methods**
Sources fall into three categories:
- Scraped via requests + BeautifulSoup: sources 1, 2, 3, 4, 10, 12, 13
- Downloaded and extracted via pdfplumber: source 5 (Quick Facts PDF), sources 6–9 (Reddit threads saved as PDF via browser print)
- Fetched via WebFetch and saved manually: source 11 (Data USA — JS-rendered, not scrapable)

**Reddit sources (6–9) collected as PDFs**
Reddit blocks all programmatic access (direct requests, JSON API, mirror sites all return 403 or bot-protection pages). Workaround: open each thread in browser, print to PDF (Cmd+P → Save as PDF), extract text with pdfplumber.

**Dropped sources**
- Niche.com — JavaScript-rendered, scraping unreliable
- Rate My Professors — blocks scrapers entirely
- Career fair event pages — single event listings, no lasting content
- CUNY Jobs listing page — live job board, changes daily
