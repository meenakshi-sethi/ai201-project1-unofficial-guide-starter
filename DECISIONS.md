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
