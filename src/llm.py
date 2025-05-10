import shutil
import subprocess
import sys
import time
import asyncio

from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


OLLAMA_URL = "http://localhost:11434"
MODEL = "deepseek-coder:1.3b-instruct"


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


# Initialize LangChain Ollama LLM
ollama_llm = OllamaLLM(
    model=MODEL,
    base_url=OLLAMA_URL,
)


async def ask_local(prompt: str) -> str | None:
    """
    Send a prompt to Ollama using LangChain.
    Returns the completion text.
    """
    start = time.time()

    # Create a LangChain chain
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content="You are a helpful AI code/project assistant."),
            HumanMessage(content="{input}"),
        ]
    )

    chain = chat_prompt | ollama_llm | StrOutputParser()

    # Execute in a separate thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: chain.invoke({"input": prompt}))

    print(f"⏱️ Step -LLM- took {time.time() - start:.2f}s", file=sys.stderr)
    return response
