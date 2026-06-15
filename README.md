# The Unofficial Guide: Project 1

---

## Domain

Student experience at John Jay College of Criminal Justice (CUNY): clubs, research opportunities, scholarships, graduation rates, career outcomes, on-campus jobs, and what current and former students actually say about the school. Most of this information is spread across unrelated official pages or buried in Reddit threads, so there's no single place to go if you're a new or prospective student trying to understand what John Jay is really like.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Student Organizations | Official | https://www.jjay.cuny.edu/student-life/center-student-involvement-leadership/student-organizations |
| 2 | PRISM Research Program | Official | https://www.jjay.cuny.edu/research/student-research/program-research-initiatives-science-math |
| 3 | Honors & Achievement Programs | Official | https://www.jjay.cuny.edu/academics/undergraduate-programs/honors-achievement-programs |
| 4 | Research & Creativity Scholarships | Official | https://www.jjay.cuny.edu/research/student-research/office-student-research-creativity/research-creativity-scholarships/undergraduategraduate-researchcreativity-assistant-scholarship |
| 5 | Quick Facts 2023 PDF | Official | https://www.jjay.cuny.edu/sites/default/files/2024-05/QUICK%20FACTS%202023.pdf |
| 6 | r/CUNY — "Is John Jay a good school?" | Reddit | https://reddit.com/r/CUNY/comments/1gwtc86 |
| 7 | r/CUNY — "First Semester At John Jay" | Reddit | https://reddit.com/r/CUNY/comments/kj7zc4 |
| 8 | r/CUNY — "First day tomorrow..." | Reddit | https://reddit.com/r/CUNY/comments/1f2r9wf |
| 9 | r/CUNY — "Any 5-10 year graduates?" | Reddit | https://reddit.com/r/CUNY/comments/1gzmx74 |
| 10 | College Factual — Graduation/Retention | Third-party | https://www.collegefactual.com/colleges/cuny-john-jay-college-of-criminal-justice/academic-life/graduation-and-retention/ |
| 11 | Data USA — John Jay Profile | Third-party | https://datausa.io/profile/university/cuny-john-jay-college-of-criminal-justice |
| 12 | Career Building & Job Search | Official | https://www.jjay.cuny.edu/student-life/career-building-job-search |
| 13 | Federal Work-Study | Official | https://www.jjay.cuny.edu/admissions/tuition-financial-aid/federal-work-study |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters, snapped to the nearest word boundary so no chunk starts mid-word

**Why these choices fit my documents:**
I skimmed all 13 documents before picking these numbers. Most entries are short. A club description is around 150–250 chars, a FAQ answer is 200–300 chars, a Reddit comment is 150–300 chars. 300 chars fits one entry cleanly without merging unrelated ones. Going smaller would split FAQ pairs mid-answer. Going larger would combine multiple entries into one chunk, which hurts retrieval because the system would return a chunk that's about two different topics at once.

I used recursive character splitting instead of fixed-size. The difference: fixed-size cuts at exactly 300 chars no matter what. Recursive tries paragraph breaks first, then sentence endings, then word boundaries, and only falls back to a hard cut if nothing else works. My corpus is mixed (stats pages, FAQ pages, Reddit threads) so I needed something that adapts to each document's structure rather than brute-forcing the same cut everywhere.

**Final chunk count:** 765 chunks across 13 documents

---

## Chunking Strategy Comparison

During Milestone 4 retrieval testing, I ran the same 5 evaluation queries against chunk sizes 300, 350, 400, 450, and 500 to see whether larger chunks improved retrieval distances. Results below show top-1 distance per query (lower = better match):

| Query | 300 chars | 400 chars | 500 chars |
|-------|-----------|-----------|-----------|
| Q1 — total enrollment | 0.5961 | 0.7473 | 0.7283 |
| Q2 — 6-year graduation rate | **0.3908** | **0.4526** | **0.4829** |
| Q3 — FWS eligibility | 0.7599 (wrong source) | 0.8252 (wrong source) | 0.6936 (right source) |
| Q4 — PRISM program | 0.5103 | 0.5103 | 0.5345 |
| Q5 — Reddit transfer opinions | 0.8282 | 0.8769 | 0.9833 |

**Which strategy performed better and why:**

300 chars wins overall. Q2 and Q4 both get their best distances at 300. Q1 (enrollment) and Q5 (Reddit) get progressively worse as chunk size increases. Larger chunks merge unrelated stats or multiple short Reddit comments into one embedding, which dilutes the semantic signal.

500 chars helps Q3 (FWS eligibility) find the right source document, but the distance is still 0.69, which is above the 0.5 threshold and not a meaningful improvement for generation quality.

The one case where larger chunks would clearly help is Q3: the FAQ format splits the eligibility question from the answer across chunk boundaries. A 500-char chunk is more likely to keep them together. But this benefit for one query doesn't outweigh the degradation on Q1 and Q5.

**Final decision:** 300 chars with 50-char overlap, recursive splitting. Best performance on 4 of 5 queries.

---

**Sample chunks:**

**Chunk 1** — `01_student_organizations.txt` (chunk #10)
> The purpose of this club is to enhance the criminological and sociological interest and awareness of the John Jay community. Our mission is to educate and provide opportunities for students of the John Jay community through educational events, networking events, and conferences, etc.

**Chunk 2** — `05_quick_facts_2023.txt` (chunk #0)
> Quick Facts 2023. Fall 2023 Total Student Enrollment: 13,465. 11,656 Total Undergraduates. 1,809 Total Graduates.

**Chunk 3** — `13_federal_work_study.txt` (chunk #8)
> Be a citizen of the United States or an eligible non-citizen as per the program guidelines. Meet Satisfactory Academic Progress (SAP). Complete the Orientation with Career and Professional Development (Good for two years)

**Chunk 4** — `06_reddit_is_jjay_good.txt` (chunk #3)
> Really good school and 100% recommend! Just graduated last spring with my BA in Criminal Justice and from the Honors Program and honestly it was some of the best 4 years. There's a lot of opportunities for

**Chunk 5** — `02_prism_research.txt` (chunk #4)
> as scientists and future professionals and to expose them to opportunities for further training and growth. The National Science Foundation, the National Academy of Sciences and CUNY all recognized PRISM as a model of excellence for

---

## Retrieval

**Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers | **Top-k:** 4

**Test 1 — What is the 6-year graduation rate at John Jay?**

| Rank | Distance | Source | Chunk (truncated) |
|------|----------|--------|-------------------|
| 1 | 0.3908 | `10_college_factual_graduation.txt` | a four-year graduation rate of 23%, first-time students in the John Jay class of 2015 who attended classes full-time were less likely than average to graduate on time. After six years, the John Jay graduation rate was 46%... |
| 2 | 0.4434 | `10_college_factual_graduation.txt` | First-Time / Part-Time John Jay Graduation Rates vs. National Average. Four Years 4%, Six Years 21%, Eight Years 29% |
| 3 | 0.4616 | `10_college_factual_graduation.txt` | Six Year Graduation Rate 62 out of 100. John Jay Non First-Time / Full-Time Graduation Rate vs. National Average. Six Years 62%... |
| 4 | 0.4679 | `10_college_factual_graduation.txt` | Six Year Graduation Rate 46 out of 100. First-Time / Full-Time Completions. John Jay Four Years 23%, Six Years 46% |

**Why these chunks are relevant:** All 4 results are from College Factual's graduation page, which is exactly the right source. The top chunk explicitly states "After six years, the John Jay graduation rate was 46%", which is a direct answer to the query. Distances are all below 0.5, which means the model found a strong semantic match between the query and the chunk content.

---

**Test 2 — What is the PRISM program at John Jay?**

| Rank | Distance | Source | Chunk (truncated) |
|------|----------|--------|-------------------|
| 1 | 0.5103 | `02_prism_research.txt` | How has PRISM made your John Jay experience fulfilling? PRISM has given me the opportunity to get real hands-on research experience, make friends, and discover my passion. |
| 2 | 0.6161 | `02_prism_research.txt` | Once I was at the College, I joined PRISM, and through the research projects I conducted, I grew to really like toxicology and decided to major in the field. |
| 3 | 0.7378 | `02_prism_research.txt` | senior who is earning a bachelor's degree in cell and molecular biology. "It's why I came to John Jay and joined PRISM, because I knew it would put me on the path to career success." |
| 4 | 0.7545 | `03_honors_programs.txt` | Program for Research Initiatives for Science and Math (PRISM) provides an opportunity for forensic science, math and computer science students to engage in scientific research while completing their degree. |

**Why these chunks are relevant:** All 4 results come from the two most relevant sources: the PRISM research page and the honors programs page. Chunk 4 is the program description that directly answers the query. Chunks 1–3 are student testimonials that add context about what PRISM does in practice. The model picked up on "PRISM" and "John Jay" across both sources.

---

**Test 3 — Who is eligible for the Federal Work-Study program at John Jay?**

| Rank | Distance | Source | Chunk (truncated) |
|------|----------|--------|-------------------|
| 1 | 0.7599 | `04_scholarships.txt` | with a John Jay College faculty member over the course of (1) year (September to end of May) |
| 2 | 0.8328 | `13_federal_work_study.txt` | Finally, you could be hired as a regular employee by the employer for whom you worked as a Federal Work-Study student. Is there a Federal Work Study Waitlist? Yes. |
| 3 | 0.8458 | `13_federal_work_study.txt` | eligible for participation in the FWS Program. Entering freshmen will not be eligible to participate in the Federal Work-Study program until the beginning of their entering Fall/Spring semester. |
| 4 | 0.8605 | `13_federal_work_study.txt` | is awarded on a first-come, first-served basis. John Jay College receives a fixed amount of money each academic year to make FWS awards. |

The top result is off-topic. It comes from the scholarships document, not the FWS FAQ. Chunks 2–4 are from the right source and contain eligibility-related content, but distances above 0.8 indicate the model is not making a strong semantic connection between "who is eligible" and the FAQ-style answer text. This is a retrieval weakness I noted in my evaluation. Thin FAQ documents produce few chunks and the dense question-answer format doesn't embed as cleanly as prose.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers. Runs locally with no API key and no rate limits. Its 256-token context window fits cleanly within the 300-char chunks I'm using, so no truncation happens during embedding.

**Production tradeoff reflection:**
For a real deployment I'd weigh a few things. First, context length. `all-MiniLM-L6-v2` handles 256 tokens, which is fine for 300-char chunks but would truncate longer documents. `text-embedding-3-large` from OpenAI supports 8,191 tokens, which matters if chunk size ever increases. Second, multilingual support. Nearly half of John Jay students are Hispanic and a significant share are first-generation, so queries in Spanish are realistic. `multilingual-e5-large` handles this; `all-MiniLM-L6-v2` does not. Third, accuracy. Larger models like `text-embedding-3-large` produce better semantic matches on domain-specific text, which would have helped with the retrieval failures I saw on factual lookup queries (Q1 enrollment) and FAQ-style documents (Q3 FWS). Fourth, latency and cost. API-hosted models add network round-trips and per-token costs that matter at scale. For this project, local and free was the right call. For production with real users, I'd test `text-embedding-3-large` first and fall back to a local model only if cost became a constraint.

---

## Metadata Filtering

The `retrieve()` function accepts an optional `source_filter` parameter, which is a list of source filenames to restrict results to. Two presets are defined in `embed.py`: `REDDIT_SOURCES` (the 4 Reddit thread files) and `OFFICIAL_SOURCES` (the 9 official/third-party files).

**Query:** "What do students think about John Jay College?"

**No filter — all sources:**
| Distance | Source | Chunk |
|----------|--------|-------|
| 0.5699 | `02_prism_research.txt` | nothing but great things to say about the College. That gave me the green light to go for what I want |
| 0.5886 | `02_prism_research.txt` | What advice do you have for incoming John Jay students? |
| 0.6007 | `02_prism_research.txt` | I initially wanted to work in law enforcement, so John Jay was always on my radar... |
| 0.6594 | `06_reddit_is_jjay_good.txt` | 87 lol not that good. I personally... |

**Reddit sources only (`source_filter=REDDIT_SOURCES`):**
| Distance | Source | Chunk |
|----------|--------|-------|
| 0.6594 | `06_reddit_is_jjay_good.txt` | 87 lol not that good. I personally... |
| 0.7400 | `06_reddit_is_jjay_good.txt` | Is John Jay a good school? I recently got accepted into John Jay through on-site admissions... |
| 0.7524 | `06_reddit_is_jjay_good.txt` | do so, but other than that it's decent. I started loving John Jay once I finally got done with my prereqs |
| 0.9396 | `06_reddit_is_jjay_good.txt` | not bad. Wow! Thank you for giving me your experience... |

**Official sources only (`source_filter=OFFICIAL_SOURCES`):**
| Distance | Source | Chunk |
|----------|--------|-------|
| 0.5699 | `02_prism_research.txt` | nothing but great things to say about the College... |
| 0.5886 | `02_prism_research.txt` | What advice do you have for incoming John Jay students? |
| 0.6007 | `02_prism_research.txt` | I initially wanted to work in law enforcement, so John Jay was always on my radar... |
| 0.6673 | `02_prism_research.txt` | Queensborough Community College before transferring to John Jay through the CUNY Justice Academy |

The filter has a visible effect. Reddit-only returns raw student opinions from Reddit threads, while official-only returns institutional content and student testimonials from the PRISM page. A user who wants unfiltered student sentiment gets Reddit chunks; a user who wants verified institutional information gets official source chunks.

---

## Grounded Generation

**How grounding is enforced:**

The system prompt in `generate.py` tells the model to use only what's in the retrieved context and nothing else. The key line is:

> "Answer the question using ONLY the information provided in the context below. Do not use any outside knowledge or make anything up. If the context does not contain enough information to answer the question, respond with exactly: 'I don't have enough information in my sources to answer that question.'"

I capitalized ONLY so there's no ambiguity, and gave the refusal phrase word-for-word so the model doesn't water it down. The sources shown in the UI come from the pipeline code, not from the model. After the model answers, `generate.py` collects the source filenames and URLs from the retrieved chunks and returns them separately. The model never writes the source list itself.

**Example response 1 — graduation rate:**

> "The 6-year graduation rate at John Jay is 46% for first-time, full-time students, and 52% overall."

Retrieved from: `10_college_factual_graduation.txt`: https://www.collegefactual.com/colleges/cuny-john-jay-college-of-criminal-justice/academic-life/graduation-and-retention/

**Example response 2 — PRISM program:**

> "The PRISM program at John Jay is the Program for Research Initiatives for Science and Math, which provides an opportunity for forensic science, math, and computer science students to engage in scientific research while completing their degree."

Retrieved from: `02_prism_research.txt`, `03_honors_programs.txt`

**Out-of-scope refusal:**

Query: "What is the weather like on Mars?"

> "I don't have enough information in my sources to answer that question."

Nothing in the retrieved chunks is about Mars, so the model refuses instead of making something up.

---

## Query Interface

The UI runs with `python app.py` and opens at `http://localhost:7860`. It's built with Gradio.

**Input:** One text box where you type your question. Hit Enter or click Ask.

**Output:**
- **Answer**: what Groq's `llama-3.3-70b-versatile` generated from the retrieved chunks
- **Retrieved from**: the source files and URLs the answer came from

The page also has a short description of what the guide covers and a list of example questions, so someone opening it for the first time knows what to ask without needing to read any documentation.

**Sample interaction:**

> **Question:** What is the 6-year graduation rate at John Jay?
>
> **Answer:** The 6-year graduation rate at John Jay is 46% for first-time, full-time students, and 52% overall.
>
> **Retrieved from:**
> • 10_college_factual_graduation.txt: https://www.collegefactual.com/colleges/cuny-john-jay-college-of-criminal-justice/academic-life/graduation-and-retention/

---

## Evaluation Report

---

### Q1 — What is the total student enrollment at John Jay College as of Fall 2023?

| | |
|---|---|
| **Expected** | 13,465 total students (11,656 undergraduates, 1,809 graduates) — from Quick Facts 2023 PDF |
| **System returned** | "I don't have enough information in my sources to answer that question." |
| **Retrieval quality** | Off-target — top 4 chunks came from scholarships and College Factual, not Quick Facts. The correct chunk ranked 9th, outside the retrieval window |
| **Accuracy** | ❌ Inaccurate |

---

### Q2 — What is the 6-year graduation rate at John Jay?

| | |
|---|---|
| **Expected** | 46% for first-time, full-time students and 52% overall — from College Factual graduation page. (Note: Quick Facts 2023 reports 55.5% for the Fall 2017 cohort and Data USA reports 54%–55.8%; differences are due to varying methodology and cohort year. The system retrieves College Factual, so its figures are the correct reference for grading.) |
| **System returned** | "The 6-year graduation rate at John Jay is 46% for first-time, full-time students, and 52% overall." |
| **Retrieval quality** | Relevant — all 4 chunks from College Factual graduation page, all distances below 0.5 (top chunk: 0.39) |
| **Accuracy** | ✅ Accurate — answer matches the retrieved source with the correct figures for that source |

---

### Q3 — Who is eligible for the Federal Work-Study program at John Jay?

| | |
|---|---|
| **Expected** | Must be a US citizen or eligible non-citizen, complete the FAFSA and check the FWS box, awarded first-come first-served. International students and entering freshmen (until their first semester begins) are not eligible |
| **System returned** | "Entering freshmen are not eligible until the beginning of their entering Fall/Spring semester, but other students are eligible." |
| **Retrieval quality** | Partially relevant — 1 of 4 chunks from the correct FWS document, 1 from scholarships; distances ranged 0.76–0.86 |
| **Accuracy** | ⚠️ Partially accurate — captures the freshmen exclusion but misses the FAFSA requirement, citizenship criteria, and first-come first-served detail |

---

### Q4 — What is the PRISM program at John Jay?

| | |
|---|---|
| **Expected** | PRISM is a STEM undergraduate research program. Over 800 undergrads have participated. It includes a Transfer Together Program for students transferring from CUNY community colleges |
| **System returned** | "PRISM is the Program for Research Initiatives for Science and Math, providing forensic science, math, and computer science students opportunities to engage in scientific research while completing their degree." |
| **Retrieval quality** | Relevant — chunks from PRISM page and honors programs page (top distance: 0.51), but retrieval surfaced student testimonial chunks instead of the program stats chunks |
| **Accuracy** | ⚠️ Partially accurate — correct definition and field, but missing the 800+ participants figure and the Transfer Together Program |

---

### Q5 — What do Reddit users say about transferring to John Jay?

| | |
|---|---|
| **Expected** | Transfer students mention transferring from CUNY community colleges (BCC, BMCC), using the ASAP program, and a student-run Discord with 100+ transfer and freshman students — from Reddit threads 06, 07, 08 |
| **System returned** | "I don't have enough information in my sources to answer that question." |
| **Retrieval quality** | Off-target — top chunk came from the PRISM page, not the Reddit transfer threads. The right chunks never made it into the top 4 |
| **Accuracy** | ❌ Inaccurate |

---

**Summary:** 1 accurate (Q2), 2 partially accurate (Q3, Q4), 2 inaccurate (Q1, Q5)

---

## Failure Case Analysis

### Failure 1 — Enrollment number not found

**Question:** "What is the total student enrollment at John Jay College as of Fall 2023?"

**System returned:** "I don't have enough information in my sources to answer that question."

The answer (13,465 students) is in `05_quick_facts_2023.txt` but retrieval never surfaced it. The right chunk ranked 9th, not in the top 4.

**Why it failed (retrieval stage):** The Quick Facts PDF is one dense page of bullet stats with no sentences, just numbers and labels. At 300 chars per chunk, you get things like "13,465. 11,656 Total Undergraduates. 1,809 Total Graduates." The embedding model needs surrounding words to understand meaning, and there aren't any here. The query "total student enrollment" has a clear meaning, but the chunk it needs to match is mostly numbers so the model doesn't connect them. Distance was 0.60, outside the retrieval window.

**Fix:** Hybrid search. BM25 keyword matching would find "student enrollment: 13,465" by exact words regardless of what the embedding thinks.

---

### Failure 2 — FWS eligibility answer is incomplete

**Question:** "Who is eligible for the Federal Work-Study program at John Jay?"

**System returned:** "Entering freshmen are not eligible until the beginning of their entering Fall/Spring semester, but other students are eligible."

That's only one part of the answer. The full criteria (US citizen or eligible non-citizen, complete FAFSA, awards are first-come first-served) never showed up.

**Why it failed (chunking stage):** The FWS document is a 20+ question FAQ. Each Q and its A are short enough that the 300-char chunker often puts the question in one chunk and the answer in the next. When I ask "who is eligible," retrieval finds chunks that match the question phrasing, not the answer phrasing. The eligibility criteria chunk ("Be a US citizen or eligible non-citizen…") is in the document but it didn't score high enough to make the top 4 because it doesn't sound much like the question. Distances ranged 0.76–0.86, which is weak.

**Fix:** Keep each FAQ Q+A pair as one unit instead of letting the chunker split them. Parent document retrieval or a document-aware chunker would handle this.

---

### Failure 3 — "Earn" vs "wage" — same meaning, different words

**Question:** "How much can students earn under the Federal Work-Study program?"

**System returned:** "I don't have enough information in my sources to answer that question."

The answer is right there in the document: "hourly wage can range from minimum wage to $17.00 per hour." When I rephrased the question to "What are the hourly wages under Federal Work-Study?" it answered correctly.

**Why it failed (retrieval stage):** The word "earn" in my query and the word "wage" in the document mean the same thing, but the embedding model placed them far enough apart in vector space that the right chunk didn't make the top 4. The model instead found chunks about FWS award earning limits, which use "earn" in a different sense. This is the core limitation of pure semantic search. Word choice matters more than it should.

**Fix:** Hybrid search. BM25 would find "earn" and "wage" appearing together in the same sentence regardless of how the embedding model treats them as concepts.

---

## Spec Reflection

**One way the spec helped:**

Writing `planning.md` before any code forced me to actually read through all 13 documents and think about their structure. That's how I landed on 300 chars. I noticed most entries (club descriptions, FAQ answers, Reddit comments) run 150–300 chars, so one chunk per entry made sense. When I ran the chunker and found 101 chunks over 300 chars, I had something concrete to fix toward. Without a written target I might not have caught that at all and moved on thinking the chunker was fine.

**One way it diverged:**

I planned to use an in-memory ChromaDB client. Once the full app was running, restarting it meant re-embedding all 765 chunks every time, about 10 seconds. I switched to `chromadb.PersistentClient()` so the index saves to disk and loads in under 2 seconds on subsequent runs. That wasn't in the original plan; it only became obvious once I was actually using the app and restarting it repeatedly while testing.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline**

- *What I gave the AI:* The Chunking Strategy section from `planning.md` with chunk size 300, overlap 50, recursive character splitting, and a description of the 13 document types.
- *What it produced:* `ingest.py` with `load_documents`, `clean_text`, and `_recursive_split`. The structure was right but had two bugs. When overlap text combined with a new part exceeded 300 chars it silently saved the oversized result as `current`, and the last chunk in the loop was appended without a size check.
- *What I changed or overrode:* I ran the chunker, counted the output, and found 101 of 767 chunks were over 300 chars (max was 1,132). I pointed Claude to both bugs specifically and directed the fixes: check `len(overlap + part) <= chunk_size` before setting `current`, and re-split if the final chunk is oversized. I also added "Image" to the boilerplate skip list after spotting standalone "Image" chunks coming from `<img alt="Image">` tags in scraped pages.

**Instance 2 — Generation and Gradio UI**

- *What I gave the AI:* The architecture diagram from `planning.md`, the grounding requirement (answer only from retrieved context, include source attribution), and the Gradio skeleton from the project instructions.
- *What it produced:* `generate.py`, `query.py` as an end-to-end wrapper, and `app.py`. The system prompt said "try to answer only from the documents," which is too soft and easy to ignore.
- *What I changed or overrode:* I changed "try to answer only" to "Answer using ONLY" and added the exact refusal phrase word-for-word so the model doesn't soften it on its own. I also directed the switch from in-memory ChromaDB to `PersistentClient` after noticing the app re-embedded all 765 chunks on every restart. I tested the out-of-scope refusal with "What is the weather like on Mars?" before calling the milestone done.
