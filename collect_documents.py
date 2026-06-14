"""Collect all 13 source documents into documents/."""
import io
import os
import requests
import pdfplumber
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_text(url, filepath):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    lines = [l for l in soup.get_text(separator="\n", strip=True).splitlines() if l.strip()]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: {url}\n\n" + "\n".join(lines))
    print(f"Saved {filepath}")


def fetch_pdf(url, filepath):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        text = "\n\n".join(p.extract_text() for p in pdf.pages if p.extract_text())
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: {url}\n\n{text}")
    print(f"Saved {filepath}")


def extract_pdf_to_txt(pdf_path, txt_path, source_url=""):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n\n".join(p.extract_text() for p in pdf.pages if p.extract_text())
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: {source_url}\n\n{text}" if source_url else text)
    print(f"Saved {txt_path}")


if __name__ == "__main__":
    os.makedirs("documents", exist_ok=True)

    # Web sources
    fetch_text("https://www.jjay.cuny.edu/student-life/center-student-involvement-leadership/student-organizations", "documents/01_student_organizations.txt")
    fetch_text("https://www.jjay.cuny.edu/research/student-research/program-research-initiatives-science-math", "documents/02_prism_research.txt")
    fetch_text("https://www.jjay.cuny.edu/academics/undergraduate-programs/honors-achievement-programs", "documents/03_honors_programs.txt")
    fetch_text("https://www.jjay.cuny.edu/research/student-research/office-student-research-creativity/research-creativity-scholarships/undergraduategraduate-researchcreativity-assistant-scholarship", "documents/04_scholarships.txt")
    fetch_pdf("https://www.jjay.cuny.edu/sites/default/files/2024-05/QUICK%20FACTS%202023.pdf", "documents/05_quick_facts_2023.txt")
    fetch_text("https://www.collegefactual.com/colleges/cuny-john-jay-college-of-criminal-justice/academic-life/graduation-and-retention/", "documents/10_college_factual_graduation.txt")
    fetch_text("https://www.jjay.cuny.edu/student-life/career-building-job-search", "documents/12_career_building.txt")
    fetch_text("https://www.jjay.cuny.edu/admissions/tuition-financial-aid/federal-work-study", "documents/13_federal_work_study.txt")

    # Reddit PDFs (saved manually via browser print to documents/)
    extract_pdf_to_txt("documents/06_reddit_is_jjay_good.pdf", "documents/06_reddit_is_jjay_good.txt", "https://reddit.com/r/CUNY/comments/1gwtc86")
    extract_pdf_to_txt("documents/07_reddit_first_semester.pdf", "documents/07_reddit_first_semester.txt", "https://reddit.com/r/CUNY/comments/kj7zc4")
    extract_pdf_to_txt("documents/08_reddit_first_day.pdf", "documents/08_reddit_first_day.txt", "https://reddit.com/r/CUNY/comments/1f2r9wf")
    extract_pdf_to_txt("documents/09_reddit_graduates.pdf", "documents/09_reddit_graduates.txt", "https://reddit.com/r/CUNY/comments/1gzmx74")

    # Data USA: already saved as 11_data_usa_jjay.txt via WebFetch
    print("Note: 11_data_usa_jjay.txt was collected via WebFetch and is already saved.")
    print("\nAll documents collected.")
