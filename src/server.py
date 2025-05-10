from typing import Optional
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys
import asyncio

from embedder import index_code_chunks
from search import search_code
from llm import ask_local, ensure_model_ready
from config import CODE_EXTENSIONS


def log(msg):
    print(f"[orellis] {msg}", file=sys.stderr)


# Ensure the model is ready
ensure_model_ready()

# Create the MCP server
app = FastMCP("orellis")

# In-memory cache keyed by project path
_project_cache = {}


@app.resource("project://files/{project_path}")
def list_files(project_path: str) -> list[str]:
    log(f"📁 Listing files in {project_path}")
    root = Path(project_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project path {project_path} does not exist")

    files = []
    for ext in CODE_EXTENSIONS:
        files.extend(
            [
                str(p.relative_to(root))
                for p in root.rglob(f"*{ext}")
                if not any(
                    ex in p.parts
                    for ex in [".venv", ".git", "node_modules", "__pycache__"]
                )
            ]
        )
    return files


@app.resource("code:///{full_path}")
def get_code(full_path: str) -> str:
    p = Path(full_path).resolve()
    # optional: lock down to a safe directory, etc.
    return p.read_text(encoding="utf‑8")


def get_indexed_code(project_path: str):
    log(f"🧠 Getting indexed code for {project_path}")
    if project_path in _project_cache:
        return _project_cache[project_path]

    # Get list of file paths
    files = list_files(project_path)

    # Create vectorstore directly from files
    vectorstore = index_code_chunks(files, project_path)

    # Store in cache
    _project_cache[project_path] = vectorstore
    return vectorstore


@app.tool()
async def ask_codebase(project_path: str, question: str) -> str | None:
    "Ask a natural-language question about the codebase"
    log(f"🤖 ask_codebase: {question} on {project_path}")

    vectorstore = get_indexed_code(project_path)
    context_chunks = search_code(question, vectorstore)

    # Assemble context into a single prompt
    context_str = "\n\n---\n\n".join(
        [f"# File: {path}\n{code}" for path, code in context_chunks]
    )
    prompt = (
        f"Use the following context to answer the question clearly.\n\n"
        f"{context_str}\n\n---\n\n"
        f"Question: {question}\n"
    )
    return await ask_local(prompt)


@app.tool()
async def onboarding_walkthrough(
    project_path: str, focus_dir: Optional[str] = None, max_files: Optional[int] = None
) -> str:
    "Generate a summary of the codebase for onboarding"
    log(f"🚀 Starting walkthrough for {project_path}")

    # Get project files, optionally filtered by directory
    files = list_files(project_path)
    if focus_dir:
        files = [f for f in files if f.startswith(focus_dir)]

    # Allow limiting the number of files for large projects
    if max_files and len(files) > max_files:
        log(f"Limiting analysis to {max_files} files out of {len(files)} total")
        files = files[:max_files]

    # Group files by directory for better organization
    files_by_dir = {}
    for file_path in files:
        dir_path = Path(file_path).parent.as_posix()
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(file_path)

    # First, generate project overview using directory structure
    dir_structure = "\n".join(
        [f"- {dir_path}/ ({len(files)})" for dir_path, files in files_by_dir.items()]
    )
    overview_prompt = f"""
    You're analyzing a codebase with the following structure:
    
    {dir_structure}
    
    Based on this directory structure alone, provide a high-level overview of what this 
    project might be about and how it's organized. Keep it brief (2-3 paragraphs).
    """

    # Process files by directory to maintain context
    dir_tasks = []
    for dir_path, dir_files in files_by_dir.items():
        # Get content for all files in this directory
        dir_contents = []
        for file_path in dir_files:
            try:
                content = get_code(f"{project_path}/{file_path}")
                dir_contents.append((file_path, content))
            except Exception as e:
                log(f"Error reading {file_path}: {str(e)}")

        # Create a prompt that analyzes files in this directory together
        if dir_contents:
            dir_prompt = f"Analyze these related files from directory '{dir_path}':\n\n"
            for path, code in dir_contents:
                dir_prompt += f"--- FILE: {path} ---\n{code}\n\n"

            dir_prompt += "\nProvide a summary of this directory's purpose and how these files work together. For each file, give 1-2 sentences about its role."
            dir_tasks.append(ask_local(dir_prompt))

    # Execute all tasks
    overview_task = ask_local(overview_prompt)
    dir_summaries = await asyncio.gather(overview_task, *dir_tasks)

    # Format the output
    overview = dir_summaries[0]
    section_summaries = dir_summaries[1:]

    # Create a structured output
    if not overview:
        overview = "A Problem as occured, No overview generated."

    out = ["# Project Overview\n\n" + overview + "\n\n", "# Codebase Walkthrough\n"]

    for i, (dir_path, _) in enumerate(files_by_dir.items()):
        if i < len(section_summaries):
            out.append(f"## Directory: {dir_path}\n{section_summaries[i]}\n")

    return "\n".join(out)


if __name__ == "__main__":
    log("🚀 Starting orellis server")
    app.run()
