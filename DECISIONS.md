# Project Decisions Log

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
