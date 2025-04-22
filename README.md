# Orellis: Local Codebase AI Assistant

> **Orellis** is a Model Context Protocol (MCP) server that lets engineers query and explore their local Python codebase via natural language. It embeds code files, indexes them with FAISS, and runs a local LLM (Ollama) on CPU for secure, private onboarding assistance.
**All inference remains CPU optimized and runs on your local machine—your codebase never leaves your laptop**

---

## 🚀 Features

- **Embeddings & Search**: Uses `sentence-transformers` + FAISS to embed and retrieve the most relevant code chunks.
- **Local LLM Inference**: Runs your quantized code model (e.g. `deepseek-coder:1.3b-instruct`) locally via Ollama.
- **MCP Server**: Exposes two tools over the MCP protocol:
  - `ask_codebase(project_path, question)`: Query the codebase.
  - `onboarding_walkthrough(project_path)`: Generate a guided overview of every file.
- **Async Support**: Parallelized LLM calls for fast walkthroughs.

---

## 📋 Prerequisites

1. **Python 3.10+**
2. **Ollama CLI** (for local model host):
   ```bash
   # macOS/Linux
   brew install ollama/ollama/ollama
   # Windows
   choco install ollama
   ```
3. **Ollama Model**: Pull your code model once:
   ```bash
   ollama pull deepseek-coder:1.3b-instruct
   ```
4. **Python Dependencies**:
   ```bash
   git clone <this-repo>
   cd <this-repo>/src
   python -m venv .venv
   source .venv/bin/activate    # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

---


## 💻 Running with Claude Desktop

1. **Install Claude Desktop**  
   - Download & install from https://claude.ai/desktop

2. **Setting Up The Configuration**
   - Start with making config file:
   ```bash
   mcp install server.py
   ```
   - Change the contents of the config file:
    - Open Claude Desktop and go to **File → Settings → Developer**.
    - Click on **Edit Config**
    - Open claude_desktop_config.json file
    - Copy this in:
    ```bash
    {
    "mcpServers": {
        "orellis": {
        "command": "<full path to the project you cloned>\\.venv\\Scripts\\python.exe",
        "args": [
            "<full path to the project you cloned>\\src\\server.py"
        ]
        }
        }
    }
    ```
3. **Interact**
    - Restart claude desktop completely
    - Wait till you see this:
       <img width="555" alt="Screenshot 2025-04-22 121927" src="https://github.com/user-attachments/assets/7ed678b9-5ac8-4348-bf04-f28ed0f3eb94" />

    - Provide full path of python projecct and ask a question about it or ask for a walkthrough
    - After you provide the path once  you dont need to provide it again only if you want to switch projects
   

---


## 🔄 Changing the Model

Orellis uses a local Ollama‑hosted model (`deepseek-coder:1.3b-instruct`) by default. To switch models:

1. **Pull or quantize a new model**:
   ```bash
   ollama pull <model-name>
   ```
2. **Update `llm.py`**:
   - Change `MODEL` to your new `<model-name>`.
3. **Restart the server**:
   - Restart claude desktop completely 

---


## 🔧 Performance Tips

- **Use Quantized Models**: 4-bit Q4_1 via llama.cpp or Ollama to reduce inference time ~3–4×.
- **Async Batching**: Leverage `onboarding_walkthrough`’s parallel asks to minimize wall-clock time.
- **IVF FAISS Index**: For large codebases (>10k chunks), switch to an IVF index for sub‑100 ms queries.
- **Caching**: Built-in `_project_cache` avoids re-indexing on every call.


