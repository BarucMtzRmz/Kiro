# Kiro

A local-first RAG (Retrieval-Augmented Generation) app that reads documents
from your own device and answers questions about them in a chat interface.

- **Documents stay local.** Files you index live on disk in `data/documents/`
  and are embedded into a local vector index in `data/index/` (Chroma,
  file-based, no external database).
- **Embeddings run locally.** Uses `sentence-transformers`
  (`all-MiniLM-L6-v2` by default), downloaded once and cached on your
  machine.
- **The LLM is configurable.** Defaults to [Ollama](https://ollama.com) so
  the whole pipeline — retrieval and generation — can run fully offline. You
  can instead point it at any OpenAI-compatible API (OpenAI itself, LM
  Studio, vLLM, etc.) by setting a couple of environment variables.

Supported document types: `.txt`, `.md`, `.pdf`, `.docx`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then edit if you want to change defaults
```

### LLM backend

**Option A — Ollama (fully local, default):**

```bash
# install Ollama from https://ollama.com, then:
ollama serve &
ollama pull llama3.2
```

No further config needed — `.env.example` already points at
`http://localhost:11434` with model `llama3.2`.

**Option B — OpenAI-compatible API:**

```env
KIRO_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1   # or your local server's URL
OPENAI_MODEL=gpt-4o-mini
```

## Usage

### Command line

```bash
# Index a file or an entire folder (recurses into subfolders)
python -m kiro ingest ~/Documents/notes
python -m kiro ingest ~/Documents/report.pdf

# Ask a one-off question
python -m kiro ask "What did the Q3 report say about revenue?"

# Interactive chat
python -m kiro chat

# Clear the index and start over
python -m kiro reset
```

### Web UI

```bash
streamlit run app.py
```

Upload files or point at a local folder path from the sidebar, then chat
with your documents in the main panel.

## How it works

1. **Load** — `.txt`/`.md` are read directly, `.pdf` via `pypdf`, `.docx`
   via `python-docx`.
2. **Chunk** — documents are split into overlapping ~1000-character chunks
   on paragraph boundaries (`kiro/chunking.py`), so retrieval can return
   focused passages instead of whole files.
3. **Embed + index** — each chunk is embedded with a local
   `sentence-transformers` model and stored in a persistent Chroma
   collection on disk.
4. **Retrieve** — a question is embedded the same way and matched against
   the index (cosine similarity) to pull the most relevant chunks.
5. **Generate** — the question plus retrieved chunks are sent to the
   configured LLM with a prompt instructing it to answer only from that
   context and to say when it doesn't know.

## Configuration

All settings are environment variables (see `.env.example`), including
where documents/index are stored, chunk size/overlap, how many chunks to
retrieve per question (`KIRO_TOP_K`), and which embedding model to use.

## Development

```bash
pip install pytest
pytest
```

Tests cover the chunking and document-loading logic (pure, no network or
model downloads required). Ingesting real documents does require
downloading the embedding model on first use and, for chat, a reachable
LLM backend (Ollama or an OpenAI-compatible API).
