import os, shutil
import typer
from rich import print
from typing import Optional
from crewai import Crew, Process
from config import settings
from memory import ShortTermMemory, LongTermMemory
from rag_tool import build_rag_tool
from agents import build_agents
from tasks import build_tasks

app = typer.Typer(help="Fintech Partnership CrewAI demo with coordinator, RAG, and memory.")

def _require_api_key():
    if not settings.openai_api_key:
        typer.secho("OPENAI_API_KEY is not set. Please export it and retry.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command()
def run(prompt: str, model: Optional[str] = None, topic: Optional[str] = "general", out: Optional[str] = None):
    """Propose a sector partnership idea, then run compliance & risk, output Markdown."""
    _require_api_key()

    model_name = model or settings.openai_model
    short_mem = ShortTermMemory()
    long_mem = LongTermMemory(db_path=settings.db_path)
    rag_tool = build_rag_tool(settings.knowledge_dir)

    coordinator, strategist, compliance, risk, writer = build_agents(rag_tool=rag_tool, llm_name=model_name)

    crew = Crew(
        agents=[strategist, compliance, risk, writer],
        tasks=[],
        process=Process.hierarchical,
        manager_agent=coordinator,
        verbose=True,
    )
    tasks = build_tasks(coordinator, strategist, compliance, risk, writer, prompt, short_mem)
    crew.tasks = tasks

    print("[bold cyan]Kicking off partnership crew...[/bold cyan]")
    result = crew.kickoff(inputs={"user_prompt": prompt})
    final_md = str(result)

    with open("last_report.md", "w") as f:
        f.write(final_md)

    long_mem.save(topic=topic or "general", content=f"Prompt: {prompt}\\nResult (first 450 chars): {final_md[:450]}")

    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(final_md)
        print(f"[green]Saved Markdown to[/green] {out}")
    print(final_md)

@app.command()
def recall(topic: Optional[str] = None, limit: int = 5):
    mem = LongTermMemory(db_path=settings.db_path)
    rows = mem.recall(topic=topic, limit=limit)
    for r in rows:
        print(f"[bold]{r[0]}[/bold] | topic={r[1]} | {r[2][:80]}...")

@app.command()
def ingest(path: str):
    dest_dir = settings.knowledge_dir
    os.makedirs(dest_dir, exist_ok=True)
    base = os.path.basename(path)
    dest = os.path.join(dest_dir, base)
    shutil.copy2(path, dest)
    print(f"[green]Ingested[/green] {base} into {dest_dir}")

@app.command()
def export_pdf(md_path: str, pdf_path: str):
    try:
        from weasyprint import HTML
    except Exception as e:
        typer.secho(f"WeasyPrint not available: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if not os.path.exists(md_path):
        typer.secho("Markdown file not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()

    html = md
    html = html.replace("\\n# ", "\\n<h1>").replace("\\n## ", "\\n<h2>").replace("\\n### ", "\\n<h3>")
    html = html.replace("**", "<b>").replace("* ", "• ")
    html = f"<html><body><pre style='font-family: ui-monospace, Menlo, Monaco, Consolas, monospace'>{html}</pre></body></html>"

    HTML(string=html).write_pdf(pdf_path)
    print(f"[green]Exported PDF to[/green] {pdf_path}")

if __name__ == "__main__":
    app()