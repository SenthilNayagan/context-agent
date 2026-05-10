"""
Configuration for document vectorization and embedding generation.

This module defines:
- Where source documents are loaded from
- How documents are chunked
- Which embedding backend and model are used
- Performance-related embedding parameters

It intentionally does NOT define:
- Vector index storage locations
- Publishing or retrieval behavior
- Storage mode (local vs external)
"""

from pathlib import Path


class VectorizationConfig:
    """
    Configuration for document loading, chunking, and embedding behavior.
    """

    # ------------------------------------------------------------------
    # Project root (used only for locating source documents)
    # ------------------------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    # ------------------------------------------------------------------
    # Document source configuration
    # ------------------------------------------------------------------

    # Directory containing source documents (e.g. markdown from Confluence)
    DOCS_DIR = PROJECT_ROOT / "docs"

    # File pattern for documents
    DOCS_GLOB = "*.md"

    # ------------------------------------------------------------------
    # Embedding configuration (indexing time)
    # ------------------------------------------------------------------

    # Embedding backend implementation
    # Supported values depend on embeddings.py implementation
    EMBEDDING_BACKEND = "sentence_transformers"

    # Embedding model identifier
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    # Device for embedding computation: "cpu", "cuda", "cuda:0", etc.
    # Default is CPU for maximum compatibility
    EMBEDDING_DEVICE = "cpu"

    # Threading / parallelism (best-effort, backend-dependent)
    EMBEDDING_NUM_THREADS = 4

    # ------------------------------------------------------------------
    # Chunking strategy
    # ------------------------------------------------------------------

    # Maximum chunk size (in characters or tokens, depending on splitter)
    CHUNK_SIZE = 500

    # Overlap between consecutive chunks
    CHUNK_OVERLAP = 50
