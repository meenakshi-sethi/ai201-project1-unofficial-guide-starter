# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
