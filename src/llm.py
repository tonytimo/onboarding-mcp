import shutil
import subprocess
import sys
import time
import asyncio
from ollama import AsyncClient


OLLAMA_URL = "http://localhost:11434"
MODEL = "deepseek-coder:1.3b-instruct"
client = AsyncClient(host=OLLAMA_URL)


def ensure_model_ready() -> None:
    if not shutil.which("ollama"):
        print("Ollama not found. Install it from https://ollama.com/download")
        sys.exit(1)

    try:
        result = subprocess.check_output(["ollama", "list"], text=True)
        if MODEL not in result:
            print(f"⬇️ Pulling model: {MODEL}")
            subprocess.run(["ollama", "pull", MODEL], check=True)
    except Exception as e:
        print("Failed to check/pull model:", e)
        sys.exit(1)


async def ask_local(prompt: str) -> str | None:
    """
    Send a prompt to Ollama using the AsyncClient.
    Returns the completion text.
    """
    start = time.time()
    response = await client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI code/project assistant.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    print(f"⏱️ Step -LLM- took {time.time() - start:.2f}s", file=sys.stderr)
    return response.message.content
