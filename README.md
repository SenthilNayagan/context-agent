# ContextAgent

**ContextAgent** is a **local‑first, CPU‑friendly Retrieval‑Augmented Generation (RAG) agent** designed to help individuals and teams **query and reason over private knowledge bases** stored as documents.

It enables safe, offline, and reproducible question‑answering over Markdown‑based knowledge sources such as:
- internal documentation
- runbooks
- operational guides
- policies
- technical notes
- FAQs

ContextAgent is intentionally:
- **local‑first**
- **organization‑agnostic**
- **storage‑backend neutral**

making it suitable as a reusable RAG engine for any private knowledge‑centric workflow.

---

## Security & Privacy Model

ContextAgent is **privacy‑preserving by design**.

- **All documents, embeddings, and indexes remain on the local machine or private infrastructure**.
- **No data is sent to external services or public APIs by default**.
- LLM inference runs locally via **Ollama**.
- Vector search runs locally via **FAISS**.

### Remote Indexing Model (Enterprise‑friendly)

ContextAgent supports a **shared**, **authoritative vector index** stored in:

- SharePoint
- via OneDrive‑synced local folders

This ensures:

- All access is local filesystem access
- No SharePoint APIs are used at runtime
- Index distribution is handled transparently by OneDrive sync

**Note:** Even in remote mode, ContextAgent never streams documents, embeddings, or prompts over the network at query time.

---

## Project Goals

ContextAgent is designed to:

- Ingest private Markdown documents
- Chunk and embed documents into semantic representations
- Persist embeddings in a FAISS vector index
- Enforce strict compatibility between indexing and querying
- Retrieve relevant context deterministically
- Generate answers using a local Large Language Model (LLM)
- Support local and shared (remote) index workflows
- Fail fast on misconfiguration
- Remain safe, explainable, and maintainable by design

Default execution is **CPU‑based**, with optional GPU support via configuration.

---

## Technology Stack

ContextAgent is built entirely on **open‑source**, **local‑first components**:

- **Python 3.10+** — core implementation language
- **LangChain** — document loading, chunking abstractions, vector store integration
- **Sentence‑Transformers** — default embedding backend (CPU‑friendly)
- **FAISS** — local, in‑process vector similarity search
- **Ollama** — local LLM and optional embedding runtime
- **FastAPI** — HTTP API
- **Markdown** — canonical source document format

---

## Prerequisites

Before using ContextAgent, ensure the following are available:

- **Python 3.10 or newer**
- **Virtual environment support** (`venv` recommended)
- **Ollama installed and running locally** (for LLM inference and optional embeddings)
- **5–10 GB free disk space** (depends on document size)

**Optional:** CUDA‑enabled GPU for faster embedding generation

---

## High‑Level Architecture

```text
context-agent/
├── pyproject.toml
├── README.md
├── setup.bat
├── ollama-setup.bat
│
├── docs/                           # Private knowledge base (Markdown)
│   └── *.md
│
├── .vector_build/                  # FAISS index + metadata
│   └── vector_index/
│       ├── faiss.faiss             # Vector index
│       ├── faiss.pkl               # Vector index pickel file
│       └── index_metadata.json     # Other metadata
│
├── src/
│   └── context_agent/              # Root Python package
│       ├── __init__.py
│       ├── __main__.py             # Python execution entry hook (python -m context_agent)
│       ├── main.py                 # Canonical application startup logic
│       │
│       ├── api/                    # Thin HTTP API layer (optional)
│       │   ├── __init__.py
│       │   └── server.py           # FastAPI server
│       │
│       ├── ui/                     # Optional Web UI (loosely coupled)
│       │   ├── README.md           # UI-specific notes / usage
│       │   └── static/
│       │       ├── index.html      # Web UI entry point
│       │       ├── styles.css      # UI styling (modern, minimal)
│       │       ├── app.js          # UI → API interaction logic
│       │       └── assets/
│       │           └── ba-logo.png # Branding assets (optional)
│       │
│       ├── config/                 # Configuration only (NO logic)
│       │   ├── __init__.py
│       │   ├── vector_index.py     # Index lifecycle + storage mode   
│       │   ├── vectorization.py    # Embedding + chunking config
│       │   ├── rag_query.py        # Query‑time behavior
│       │   └── ollama.py           # Ollama server config
│       │
│       ├── sources/                # Optional ingestion adapters
│       │   ├── __init__.py
│       │   └── confluence.py       # Example source adapter
│       │
│       └── rag/                    # Core RAG domain
│           ├── __init__.py
│           ├── embeddings.py       # Build + validate + publish vector index
│           └── retriever.py        # Read‑only retrieval
```
***

## Core Components

### 1. sources/confluence.py (Optional Documentation Ingestion)

Responsible for exporting Confluence pages to Markdown files locally.

**Responsibilities**

*   Fetches pages from Confluence via REST API
*   Converts HTML content to Markdown
*   Stores documents under docs/

**Notes**

*   Authentication is sourced from environment variables
*   This module is independent of RAG and embeddings

> **Why Markdown as the Source Format:** ContextAgent intentionally uses **Markdown** (**.md**) as the primary knowledge source format because it is plain‑text, structure‑preserving, and noise‑free. This results in more accurate chunking, higher‑quality embeddings, and more reliable retrieval compared to binary formats such as PDF or Word, which introduce parsing artifacts and inconsistent document structure

***

### 2. rag/embeddings.py (Indexing & Publishing)

Responsible for **building and publishing the vector index**.

**What it does**

*   Loads Markdown files from `docs/`
*   Splits content into chunks
*   Generates embeddings using a configurable backend
*   Build FAISS index locally
*   Persist metadata (`index_metadata.json`)
*   Validate index integrity
*   Publish index to authoritative storage i.e., OneDrive-synched Sharepoint (optional)

**Key characteristics**

*   Builds locally first
*   Refuses to overwrite existing local builds   
*   Publishing is explicit (`--publish`)
*   External metadata contract (`index_metadata.json`)
*   External publishing replaces the authoritative index atomically

**Note:** Any change to embeddings or chunking **requires re-indexing**.

***

### 3. rag/retriever.py (RAG Query Loop)

Responsible for **answering user questions** using the vector index.

**Responsibilities**

*   Resolve authoritative index location
*   Validate required FAISS artifacts:
    *   `faiss.faiss`
    *   `faiss.pkl`
    *   `index_metadata.json`
*   Enforce embedding compatibility
*   Load FAISS safely
*   Retrieve relevant context
*   Invoke local LLM via Ollama

**Key rules**

*   Retriever is read‑only
*   Never builds or publishes indexes
*   Works identically in local and external modes

***

### 4. config/ (Centralized Configuration)

All tunable values live under the `config/` package — **no hard-coded behavior**.

**Configuration areas include**

*   Confluence authentication and export settings
*   Vectorization parameters (chunk size, backend, model, device)
*   RAG query parameters (top-K, index location)
*   LLM runtime configuration (model, temperature, endpoint)

This design ensures:

*   Explicit configuration changes
*   Reproducible behavior
*   Fail‑fast detection of incompatible index/query combinations

***

### 5. config/vector_index.py — Index Lifecycle

Defines:

*   Storage mode:
    *   local
    *   external
*   Build directory (`.vector_build/vector_index`)
*   Authoritative index directory:
    *   Local filesystem (local mode)
    *   OneDrive‑synced SharePoint folder (external mode)

This module is the **single source of truth** for index location.

***

### 6. config/vectorization.py — Embedding Behavior

Defines:

*   Embedding backend
*   Embedding model
*   Device (CPU / GPU)
*   Chunk size and overlap

No storage logic lives here.

***

### 7. config/rag_query.py — Query‑Time Behavior

Defines:

*   TOP_K
*   Empty‑context behavior
*   Optional query‑time tuning flags

***

## Storage Modes

### Local Mode (Default)

Index stored in: `./vector_index/`

- Single‑user workflows
- No OneDrive required

### External Mode (Shared)

Set once per machine: `setx CONTEXTAGENT_STORAGE_MODE external`

- Index stored in: `%OneDrive%\AI_Knowledge_Index\vector_index`
- Requires SharePoint shortcut added to OneDrive
- OneDrive handles synchronization
- All querying remains local filesystem access

***

## Typical Workflow (External Mode)

### 1. Prepare Documents

Place Markdown files under:

```bash
docs/
```

Example:

```bash
docs/
├── deploy-process.md
├── release-guidelines.md
└── operational-faq.md
```

### 2. Admin: Build & Publish Index

```bash
rmdir /s /q .vector_build\vector_index
python embeddings.py --publish
```

This:

- Builds locally
- Validates FAISS integrity
- Publishes atomically to SharePoint

### 3. Users: Query via CLI / API / UI

`python retriever.py`

Ask questions interactively:

    Question: What's the max Redshit RPU hours set for a week and what frequency this RPU hours will be reset to zero?

or  start the API (FastAPI):

`python -m context_agent.api.server`

Open: `http://127.0.0.1:8000/docs`

***

## Embedding Backends Supported

Embedding backend selection occurs **at indexing time** and is enforced **at query time**.

### Sentence‑Transformers (Recommended)

*   Example models:
    *   `all‑MiniLM‑L6‑v2`
    *   `BAAI/bge‑base‑en‑v1.5`
*   CPU‑friendly by default
*   GPU-ready via configuration
*   Recommended for documentation RAG

### Ollama Embeddings

*   Uses embedding‑capable Ollama models
*   Fully local execution
*   Requires Ollama runtime

**Notes:** 

*   The embedding backend **cannot be changed at query time**.
*   Changing the embedding backend or model **requires re‑indexing**.
***

## Index Metadata (`index_metadata.json`)

This file acts as a **contract** between indexing and querying.

Example:

```json
{
  "embedding_backend": "sentence_transformers",
  "embedding_model": "all-MiniLM-L6-v2",
  "chunk_size": 300,
  "chunk_overlap": 30,
  "vectorizer_version": "v1"
}
```

**Why this matters**

*   Prevents silent FAISS misuse
*   Avoids querying with incompatible embeddings
*   Makes re‑indexing requirements explicit
*   Enables safe future upgrades

The metadata file is **intentionally separate** from FAISS files.

***

## When to Re‑Index

You **must** re-run indexing if you change:

*   Source documents (Important)
*   Embedding backend
*   Embedding model
*   Chunk size or overlap
*   Embedding device (CPU ↔ GPU)

You **do NOT** need to re‑index if you change:

*   LLM model
*   LLM temperature
*   Top‑K retrieval value
*   Prompt wording
*   API/UI behavior

***

## Design Principles

*   Local‑first execution
*   Explicit build → validate → publish lifecycle
*   Single source of truth for index compatibility
*   Fail‑fast validation
*   No hidden side effects
*   Clear admin vs user responsibilities
*   Enterprise‑safe shared indexing