# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student experience at John Jay College of Criminal Justice (CUNY) — clubs, research opportunities, scholarships, graduation rates, career outcomes, on-campus jobs, and what current and former students actually say about the school. Most of this information is spread across unrelated official pages or buried in Reddit threads, so there's no single place to go if you're a new or prospective student trying to understand what John Jay is really like.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Student Organizations | Official | https://www.jjay.cuny.edu/student-life/center-student-involvement-leadership/student-organizations |
| 2 | PRISM Research Program | Official | https://www.jjay.cuny.edu/research/student-research/program-research-initiatives-science-math |
| 3 | Honors & Achievement Programs | Official | https://www.jjay.cuny.edu/academics/undergraduate-programs/honors-achievement-programs |
| 4 | Research & Creativity Scholarships | Official | https://www.jjay.cuny.edu/research/student-research/office-student-research-creativity/research-creativity-scholarships/undergraduategraduate-researchcreativity-assistant-scholarship |
| 5 | Quick Facts 2023 PDF | Official | `documents/05_quick_facts_2023.txt` |
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
I skimmed all 13 documents before picking these numbers. Most entries are short — a club description is around 150–250 chars, a FAQ answer is 200–300 chars, a Reddit comment is 150–300 chars. 300 chars fits one entry cleanly without merging unrelated ones. Going smaller would split FAQ pairs mid-answer. Going larger would combine multiple entries into one chunk, which hurts retrieval because the system would return a chunk that's about two different topics at once.

I used recursive character splitting instead of fixed-size. The difference: fixed-size cuts at exactly 300 chars no matter what. Recursive tries paragraph breaks first, then sentence endings, then word boundaries — only falls back to a hard cut if nothing else works. My corpus is mixed (stats pages, FAQ pages, Reddit threads) so I needed something that adapts to each document's structure rather than brute-forcing the same cut everywhere.

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

300 chars wins overall. Q2 and Q4 both get their best distances at 300. Q1 (enrollment) and Q5 (Reddit) get progressively worse as chunk size increases — larger chunks merge unrelated stats or multiple short Reddit comments into one embedding, which dilutes the semantic signal.

500 chars helps Q3 (FWS eligibility) find the right source document, but the distance is still 0.69 — above the 0.5 threshold and not a meaningful improvement for generation quality.

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

**Why these chunks are relevant:** All 4 results are from College Factual's graduation page, which is exactly the right source. The top chunk explicitly states "After six years, the John Jay graduation rate was 46%" — a direct answer to the query. Distances are all below 0.5, which means the model found a strong semantic match between the query and the chunk content.

---

**Test 2 — What is the PRISM program at John Jay?**

| Rank | Distance | Source | Chunk (truncated) |
|------|----------|--------|-------------------|
| 1 | 0.5103 | `02_prism_research.txt` | How has PRISM made your John Jay experience fulfilling? PRISM has given me the opportunity to get real hands-on research experience, make friends, and discover my passion. |
| 2 | 0.6161 | `02_prism_research.txt` | Once I was at the College, I joined PRISM, and through the research projects I conducted, I grew to really like toxicology and decided to major in the field. |
| 3 | 0.7378 | `02_prism_research.txt` | senior who is earning a bachelor's degree in cell and molecular biology. "It's why I came to John Jay and joined PRISM, because I knew it would put me on the path to career success." |
| 4 | 0.7545 | `03_honors_programs.txt` | Program for Research Initiatives for Science and Math (PRISM) provides an opportunity for forensic science, math and computer science students to engage in scientific research while completing their degree. |

**Why these chunks are relevant:** All 4 results come from the two most relevant sources — the PRISM research page and the honors programs page. Chunk 4 is the program description that directly answers the query. Chunks 1–3 are student testimonials that add context about what PRISM does in practice. The model picked up on "PRISM" and "John Jay" across both sources.

---

**Test 3 — Who is eligible for the Federal Work-Study program at John Jay?**

| Rank | Distance | Source | Chunk (truncated) |
|------|----------|--------|-------------------|
| 1 | 0.7599 | `04_scholarships.txt` | with a John Jay College faculty member over the course of (1) year (September to end of May) |
| 2 | 0.8328 | `13_federal_work_study.txt` | Finally, you could be hired as a regular employee by the employer for whom you worked as a Federal Work-Study student. Is there a Federal Work Study Waitlist? Yes. |
| 3 | 0.8458 | `13_federal_work_study.txt` | eligible for participation in the FWS Program. Entering freshmen will not be eligible to participate in the Federal Work-Study program until the beginning of their entering Fall/Spring semester. |
| 4 | 0.8605 | `13_federal_work_study.txt` | is awarded on a first-come, first-served basis. John Jay College receives a fixed amount of money each academic year to make FWS awards. |

The top result is off-topic — it comes from the scholarships document, not the FWS FAQ. Chunks 2–4 are from the right source and contain eligibility-related content, but distances above 0.8 indicate the model is not making a strong semantic connection between "who is eligible" and the FAQ-style answer text. This is a retrieval weakness I noted in my evaluation — thin FAQ documents produce few chunks and the dense question-answer format doesn't embed as cleanly as prose.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers. Runs locally with no API key and no rate limits. Its 256-token context window fits cleanly within the 300-char chunks I'm using, so no truncation happens during embedding.

**Production tradeoff reflection:**
For a real deployment I'd weigh a few things. First, context length — `all-MiniLM-L6-v2` handles 256 tokens, which is fine for 300-char chunks but would truncate longer documents. `text-embedding-3-large` from OpenAI supports 8,191 tokens, which matters if chunk size ever increases. Second, multilingual support — nearly half of John Jay students are Hispanic and a significant share are first-generation, so queries in Spanish are realistic. `multilingual-e5-large` handles this; `all-MiniLM-L6-v2` does not. Third, accuracy — larger models like `text-embedding-3-large` produce better semantic matches on domain-specific text, which would have helped with the retrieval failures I saw on factual lookup queries (Q1 enrollment) and FAQ-style documents (Q3 FWS). Fourth, latency and cost — API-hosted models add network round-trips and per-token costs that matter at scale. For this project, local and free was the right call. For production with real users, I'd test `text-embedding-3-large` first and fall back to a local model only if cost became a constraint.

---

## Metadata Filtering

The `retrieve()` function accepts an optional `source_filter` parameter — a list of source filenames to restrict results to. Two presets are defined in `embed.py`: `REDDIT_SOURCES` (the 4 Reddit thread files) and `OFFICIAL_SOURCES` (the 9 official/third-party files).

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

The filter has a visible effect — Reddit-only returns raw student opinions from Reddit threads, while official-only returns institutional content and student testimonials from the PRISM page. A user who wants unfiltered student sentiment gets Reddit chunks; a user who wants verified institutional information gets official source chunks.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
