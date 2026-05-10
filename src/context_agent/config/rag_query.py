"""
Configuration for RAG query-time behavior.

This module defines parameters that affect how retrieval and
answer generation behave at query time.

It intentionally does NOT define:
- vector index storage locations
- embedding or chunking behavior
- publishing or build logic

Those concerns are owned by:
- config.vector_index
- config.vectorization
"""

class RagQueryConfig:
    """
    Configuration for RAG-based querying (retriever-side only).

    This config impacts:
    - how many documents are retrieved
    - how empty results are handled
    - what metadata is exposed
    """

    # ------------------------------------------------------------------
    # Retrieval parameters
    # ------------------------------------------------------------------

    # Number of nearest neighbors to retrieve from the vector index.
    # Higher values improve recall but increase prompt size.
    TOP_K = 10

    # Optional minimum relevance threshold for retrieved documents.
    # Set to None to disable score-based filtering.
    MIN_RELEVANCE_SCORE = None

    # ------------------------------------------------------------------
    # Query-time behavior flags
    # ------------------------------------------------------------------

    # If True, raise an exception when no documents are retrieved.
    # If False, allow the LLM to respond with "insufficient context".
    FAIL_ON_EMPTY_CONTEXT = False

    # If True, include document source metadata in outputs/logs.
    # Useful for debugging, auditing, or UI display.
    INCLUDE_SOURCE_METADATA = True

    # ------------------------------------------------------------------
    # Context construction hints (future-proof)
    # ------------------------------------------------------------------

    # Optional maximum size (in characters) for the combined context.
    # None means no explicit limit at this layer.
    MAX_CONTEXT_CHARS = None
