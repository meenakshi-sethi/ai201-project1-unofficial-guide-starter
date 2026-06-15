"""Gradio UI for the John Jay Unofficial Guide RAG pipeline."""
import gradio as gr
from query import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="John Jay Unofficial Student Guide") as demo:
    gr.Markdown("# John Jay College of Criminal Justice — Unofficial Student Guide")
    gr.Markdown(
        "This guide answers questions about student life at **John Jay College (CUNY)** "
        "using real documents — official college pages, Reddit threads, and third-party data. "
        "It will only answer from those sources. If the answer isn't in the documents, it will say so."
    )
    gr.Markdown(
        "**What you can ask about:**  "
        "Student clubs & organizations · Research programs (PRISM, Honors) · "
        "Scholarships · Graduation & retention rates · Federal Work-Study · "
        "Career outcomes · What current & former students say on Reddit"
    )
    gr.Markdown("---")

    with gr.Row():
        with gr.Column(scale=2):
            inp = gr.Textbox(
                label="Your question",
                placeholder="e.g. What clubs can I join at John Jay?",
                lines=2,
            )
            btn = gr.Button("Ask", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown(
                "**Example questions:**\n\n"
                "- What is the 6-year graduation rate at John Jay?\n"
                "- Who is eligible for Federal Work-Study?\n"
                "- What is the PRISM research program?\n"
                "- What honors programs does John Jay offer?\n"
                "- What do Reddit users say about John Jay?\n"
                "- What scholarships are available for undergrads?\n"
                "- What career outcomes do John Jay graduates have?"
            )

    answer = gr.Textbox(label="Answer", lines=8, interactive=False)
    sources = gr.Textbox(label="Retrieved from", lines=3, interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
