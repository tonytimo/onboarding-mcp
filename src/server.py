from faiss import IndexFlatL2
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys
import asyncio

from embedder import index_code_chunks
from search import search_code
from llm import ask_local


def log(msg):
    print(f"[orellis] {msg}", file=sys.stderr)


app = FastMCP("orellis")

# In-memory cache keyed by project path
_project_cache = {}


@app.resource("project://files/{project_path}")
def list_files(project_path: str) -> list[str]:
    log(f"📁 Listing files in {project_path}")
    root = Path(project_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project path {project_path} does not exist")
    return [
        str(p.relative_to(root))
        for p in root.rglob("*.py")
        if not any(
            ex in p.parts for ex in [".venv", ".git", "node_modules", "__pycache__"]
        )
    ]


@app.resource("code:///{full_path}")
def get_code(full_path: str) -> str:
    p = Path(full_path).resolve()
    # optional: lock down to a safe directory, etc.
    return p.read_text(encoding="utf‑8")


def get_indexed_code(
    project_path: str,
) -> tuple[list[tuple[str, str]], IndexFlatL2, list[str], list[str]]:
    log(f"🧠 Getting indexed code for {project_path}")
    if project_path in _project_cache:
        return _project_cache[project_path]

    files = list_files(project_path)
    chunks = [(fp, get_code(f"{project_path}\\{fp}")) for fp in files]
    index, texts, paths = index_code_chunks(chunks)

    _project_cache[project_path] = (chunks, index, texts, paths)
    return chunks, index, texts, paths


@app.tool()
def ask_codebase(project_path: str, question: str):
    "Ask a natural-language question about the codebase"
    log(f"🤖 ask_codebase: {question} on {project_path}")
    _, index, texts, paths = get_indexed_code(project_path)
    context_chunks = search_code(question, index, texts, paths)
    # Assemble context into a single prompt
    context_str = "\n\n---\n\n".join(
        [f"# File: {path}\n{code}" for path, code in context_chunks]
    )
    prompt = (
        f"Use the following context to answer the question clearly.\n\n"
        f"{context_str}\n\n---\n\n"
        f"Question: {question}\n"
    )
    return ask_local(prompt)


@app.tool()
async def onboarding_walkthrough(project_path: str) -> str:
    log(f"🚀 Starting walkthrough for {project_path}")
    # Load code chunks (sync)
    chunks, _, _, _ = get_indexed_code(project_path)

    # Build one prompt per file (or per batch)
    tasks = []
    for path, code in chunks:
        prompt = (
            f"Summarize this file for a new developer:\n\n"
            f"File: {path}\n"
            f"Code:\n{code}"
        )
        tasks.append(ask_local(prompt))

    # Fire them all off in parallel, await them together
    summaries = await asyncio.gather(*tasks)

    # Combine with headings
    out = []
    for (path, _), summary in zip(chunks, summaries):
        out.append(f"## {path}\n{summary}")

    return "\n\n".join(out)


if __name__ == "__main__":
    log("🚀 Starting orellis server")
    app.run()
