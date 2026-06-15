# Project 1 Planning: The Unofficial Guide
---

## Domain

Student experience at John Jay College of Criminal Justice (CUNY) — clubs, research opportunities, scholarships, graduation rates, career outcomes, on-campus jobs, and what current and former students actually say about the school. Most of this information is spread across unrelated official pages or buried in Reddit threads, so there's no single place to go if you're a new or prospective student trying to understand what John Jay is really like.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Student Organizations | Official list of 60+ clubs across 13 categories | https://www.jjay.cuny.edu/student-life/center-student-involvement-leadership/student-organizations |
| 2 | PRISM Research Program | STEM undergrad research program — includes student stories and program stats | https://www.jjay.cuny.edu/research/student-research/program-research-initiatives-science-math |
| 3 | Honors & Achievement Programs | 8 honors tracks with per-program descriptions | https://www.jjay.cuny.edu/academics/undergraduate-programs/honors-achievement-programs |
| 4 | Research & Creativity Scholarships | Scholarship eligibility, award amounts, and application criteria | https://www.jjay.cuny.edu/research/student-research/office-student-research-creativity/research-creativity-scholarships/undergraduategraduate-researchcreativity-assistant-scholarship |
| 5 | Quick Facts 2023 PDF | One-page factsheet: enrollment numbers, popular majors, student demographics | `documents/05_quick_facts_2023.txt` |
| 6 | r/CUNY — "Is John Jay a good school?" | Reddit thread with student takes on school quality | https://reddit.com/r/CUNY/comments/1gwtc86 |
| 7 | r/CUNY — "First Semester At John Jay" | Reddit thread about first-semester experiences | https://reddit.com/r/CUNY/comments/kj7zc4 |
| 8 | r/CUNY — "First day tomorrow..." | Reddit thread about first-day impressions | https://reddit.com/r/CUNY/comments/1f2r9wf |
| 9 | r/CUNY — "Any 5-10 year graduates?" | Reddit thread where alumni reflect on their outcomes | https://reddit.com/r/CUNY/comments/1gzmx74 |
| 10 | College Factual — Graduation/Retention | Graduation rates, time-to-degree, and retention stats with explanations | https://www.collegefactual.com/colleges/cuny-john-jay-college-of-criminal-justice/academic-life/graduation-and-retention/ |
| 11 | Data USA — John Jay Profile | Demographics, salary outcomes, program breakdown (collected manually — JS-rendered) | https://datausa.io/profile/university/cuny-john-jay-college-of-criminal-justice |
| 12 | Career Building & Job Search | Career stats, employer connections, notable alumni outcomes | https://www.jjay.cuny.edu/student-life/career-building-job-search |
| 13 | Federal Work-Study | FAQ on on-campus jobs: who qualifies, how to apply, pay rates | https://www.jjay.cuny.edu/admissions/tuition-financial-aid/federal-work-study |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Reasoning:** I'm using recursive character splitting. After skimming the documents, most content is short — club descriptions, FAQ pairs, Reddit comments all run about 150-300 characters. Recursive splitting tries to break at paragraph → sentence → word boundaries in that order, so it handles the mixed content without me having to treat each document differently. 300 chars keeps one entry per chunk. Fixed-size was the other option but it would cut mid-sentence on FAQ pairs which would make those chunks useless for retrieval.

**Short reviews vs long guides:** Almost everything here is short. 300 chars fits one entry cleanly. The one exception is document 08 (Reddit first day) which has longer comments — recursive handles those by splitting at sentence breaks.

**What overlap helps with:** If a key fact gets cut at the boundary (like eligibility and award amount in the same sentence), 50 chars of overlap means that sentence shows up in both chunks. I kept it at 50 and not higher because most entries stand on their own — more overlap would just repeat content.

**Too small vs too large:** If chunks were under 150, Q&A pairs would split across two chunks and neither would make sense alone. If chunks were over 600, unrelated entries would get merged and retrieval would return chunks about multiple topics at once.

**Queries this might fail for:** Questions that need info from multiple entries at once — like "compare all honors programs" — since each program is its own 300-char chunk and top-k retrieval might not surface all of them. Same problem for broad opinion questions like "what do students think overall" that need many Reddit chunks to answer well.

**Implementation note:** Overlap snaps to the nearest word boundary instead of cutting at exactly 50 chars. This prevents chunks from starting mid-word, which matters for source citations and hybrid keyword search. Overlap is slightly variable (~45–55 chars) as a result. This is standard behavior in production splitters like LangChain's RecursiveCharacterTextSplitter.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers

**Top-k:** 4

**Why this model:** Runs locally, no API key needed, no rate limits. The corpus is small and the content is general enough that a larger model like `text-embedding-3-large` wouldn't add much. Its 256-token context window also fits cleanly within the 300-char chunks I'm using.

**Why top-k 4:** Starting at 4 so relevant content is more likely to be in the retrieved set. Entries are short so 4 chunks is still focused context (~950 chars). Will tune down to 3 if retrieval starts pulling in off-topic chunks during evaluation.

**Why semantic search works without exact word match:** The model turns text into a vector based on meaning, not exact words. So "what clubs can I join" still finds chunks about "student organizations" because both mean the same thing to the model.

**Production tradeoff reflection:** With no cost constraint I'd look at `text-embedding-3-large` for better accuracy, or `multilingual-e5-large` since nearly half of John Jay students are Hispanic — multilingual support could help with non-English queries. But for a small local project, both are overkill and add API costs and latency that aren't worth it here.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the total student enrollment at John Jay College as of Fall 2023? | 13,465 total students (11,656 undergraduates, 1,809 graduates) — from Quick Facts 2023 PDF |
| 2 | What is the 6-year graduation rate at John Jay? | 55.5% for the entering class of Fall 2017 — from Quick Facts 2023 PDF (official). Data USA reports 54% 6-year completion and 55.8% overall graduation rate (slight difference due to different methodology/year) |
| 3 | Who is eligible for the Federal Work-Study program at John Jay? | Must be a US citizen or eligible non-citizen, complete the FAFSA and check the FWS box, awarded first-come first-served. International students and entering freshmen (until their first semester begins) are not eligible — from Federal Work-Study FAQ |
| 4 | What is the PRISM program at John Jay? | PRISM is a STEM undergraduate research program. Over 800 undergrads have participated. It includes a Transfer Together Program for students transferring from CUNY community colleges — from PRISM page |
| 5 | What do Reddit users say about transferring to John Jay? | Transfer students mention transferring from CUNY community colleges (BCC, BMCC), using the ASAP program, and a student-run Discord with 100+ transfer and freshman students — from Reddit threads 06, 07, 08 |

---

## Anticipated Challenges

1. **Chunk size too large for thin documents** — Sources 12 (Career Building) and 05 (Quick Facts) are only ~1,500–1,700 chars total. At 300 chars per chunk, each produces only 4–5 chunks. If a question targets those topics, retrieval has almost nothing to choose from and may return off-topic chunks instead.

2. **Broad queries will fail retrieval** — top-k=3 only surfaces 3 chunks per query. Questions that need information from multiple entries (e.g. "what opportunities are available at John Jay?") will get an incomplete answer because the pipeline can't retrieve enough context in one pass.

3. **Same stat appearing in multiple sources** — Graduation rates appear in Quick Facts (55.5%), Data USA (54%), and College Factual with slightly different numbers. The system may retrieve chunks from all three, and the LLM could produce a confused or averaged answer without knowing which source to trust.

4. **Reddit PDF extraction noise** — Chrome print-to-PDF captures UI elements (vote counts, timestamps, "Share"/"Reply" buttons). pdfplumber extracts all of it alongside the actual comment text. This noise could affect embedding quality and retrieval for Reddit-based questions.

5. **Semantic embedding as a strength for Reddit** — Reddit comments use informal, conversational language. Semantic embeddings handle this well since the model encodes meaning rather than matching exact words. A query like "is John Jay worth going to" will find relevant Reddit chunks even when the comments don't use those exact words.

---

## Architecture

```
documents/ (.txt files)
        |
        v
[ Document Ingestion ]
  requests + BeautifulSoup + pdfplumber
        |
        v
[ Chunking ]
  Recursive character split — 300 chars, 50 overlap
        |
        v
[ Embedding + Vector Store ]
  sentence-transformers (all-MiniLM-L6-v2) → ChromaDB
        |
        v
[ Retrieval ]
  ChromaDB similarity search — top-k 4
        |
        v
[ Generation ]
  Groq (llama-3.3-70b-versatile)
        |
        v
[ UI ]
  Gradio
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I gave Claude the Chunking Strategy section from planning.md and asked it to build `ingest.py` with three stages: load all `.txt` files from `documents/`, clean Reddit and web boilerplate, and split into chunks using recursive character splitting at 300 chars with 50-char overlap. It produced `load_documents`, `clean_text`, and `chunk_text` functions. I reviewed the output, found two bugs — overlap text combined with a large part silently exceeded 300 chars, and an oversized chunk at the end of the loop was appended without re-splitting — and directed both fixes. I also caught "Image" artifacts from scraped img tags and added them to the boilerplate list. Final result: 767 chunks across 13 documents, all ≤ 300 chars.

**Milestone 4 — Embedding and retrieval:**
I gave Claude the Retrieval Approach section from planning.md (model: all-MiniLM-L6-v2, top-k: 4, vector store: ChromaDB) and the architecture diagram and asked it to build `embed.py` with an embedding function and a retrieve function. I verified by running all 5 evaluation queries and checking distance scores and returned sources. 2 of 5 queries returned relevant chunks with low distances (Q2 graduation rate: 0.39, Q4 PRISM: 0.51). The 3 failing queries had documented root causes — dense PDF stats, FAQ chunking splits, and meta-query limitations. I also ran a chunk size experiment (300–500 chars) and confirmed 300 remains best overall.

**Milestone 5 — Generation and interface:**
I gave Claude the Architecture diagram, grounding requirement, and the Gradio skeleton from the project instructions and asked it to build `generate.py` and `app.py`. It produced a `generate_answer()` function that formats retrieved chunks as numbered context, passes them to Groq's `llama-3.3-70b-versatile` with a strict grounding system prompt, and returns the answer with deduplicated sources. I also created `query.py` as an end-to-end `ask()` wrapper so `app.py` stays clean. I reviewed the system prompt to confirm it enforces grounding (not just suggests it) and that source attribution is built into the return value rather than left to the LLM. I also switched ChromaDB from an in-memory client to a persistent client so re-running the app loads the existing index from disk instead of re-embedding all 765 chunks. I tested end-to-end with PRISM (accurate), FWS wages (vocabulary mismatch failure — "earn" vs "wage" — documented in DECISIONS.md), and an out-of-scope query (Mars weather — correctly refused). Final result: grounded answers with source URLs, correct out-of-scope refusal, and a Gradio UI navigable without explanation.
