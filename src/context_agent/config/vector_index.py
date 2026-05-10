"""
Vector index configuration and lifecycle management.

This module defines:
- Where the vector index is BUILT (non-authoritative)
- Where the vector index is CONSUMED (authoritative)
- How storage mode (local vs external) is resolved

It is intentionally shared by:
- embeddings.py  (producer / publisher)
- retriever.py  (consumer)

No embedding or retrieval logic should live here.
"""

import os
from pathlib import Path


class VectorIndexConfig:
    """
    Central configuration for vector index storage and lifecycle.

    STORAGE_MODE determines where the authoritative vector index lives:

    - "local":
        - Index is built and consumed locally
        - Suitable for individual / standalone usage

    - "external":
        - Index is published to and consumed from an external,
          authoritative location (e.g. OneDrive-synced SharePoint)
        - Embeddings must use --publish to update the index
    """

    # ------------------------------------------------------------------
    # Storage mode
    # ------------------------------------------------------------------

    STORAGE_MODE = os.environ.get(
        "CONTEXTAGENT_STORAGE_MODE",
        "local",   # safe default for a generic framework
    ).lower()

    # ------------------------------------------------------------------
    # Project root (used for local mode and build artifacts)
    # ------------------------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    # ------------------------------------------------------------------
    # Local build directory (NON-AUTHORITATIVE)
    #
    # - Used only by embeddings.py
    # - Never read by retriever.py
    # - Safe location for builds + validation
    # ------------------------------------------------------------------

    VECTOR_INDEX_BUILD_DIR = PROJECT_ROOT / ".vector_build" / "vector_index"

    # ------------------------------------------------------------------
    # Authoritative vector index directory
    #
    # - Used ONLY by retriever.py
    # - Embeddings publish here ONLY in external mode
    # ------------------------------------------------------------------

    if STORAGE_MODE == "external":
        # Resolve OneDrive root dynamically (corporate preferred)
        _ONEDRIVE_ROOT = Path(
            os.environ.get(
                "OneDriveCommercial",
                os.environ.get(
                    "OneDrive",
                    os.environ.get("USERPROFILE", "")
                ),
            )
        )

        if not _ONEDRIVE_ROOT:
            raise RuntimeError(
                "STORAGE_MODE=external requires OneDrive.\n"
                "Ensure OneDrive is installed and signed in."
            )

        # This folder is expected to be a OneDrive shortcut to SharePoint
        VECTOR_INDEX_DIR = (
            _ONEDRIVE_ROOT
            / "AI_Knowledge_Index"
            / "vector_index"
        )

    elif STORAGE_MODE == "local":
        VECTOR_INDEX_DIR = PROJECT_ROOT / "vector_index"

    else:
        raise RuntimeError(
            f"Unsupported STORAGE_MODE: {STORAGE_MODE}. "
            "Expected 'local' or 'external'."
        )

    # ------------------------------------------------------------------
    # Publish destination
    #
    # - Same as authoritative directory
    # - Defined explicitly for clarity and symmetry
    # ------------------------------------------------------------------

    VECTOR_INDEX_PUBLISH_DIR = VECTOR_INDEX_DIR

    # ------------------------------------------------------------------
    # Helper methods (optional, safe to use)
    # ------------------------------------------------------------------

    @classmethod
    def ensure_build_dir(cls) -> Path:
        """
        Ensure the local build directory exists.
        Used by embeddings.py.
        """
        cls.VECTOR_INDEX_BUILD_DIR.mkdir(parents=True, exist_ok=True)
        return cls.VECTOR_INDEX_BUILD_DIR

    @classmethod
    def ensure_authoritative_parent(cls) -> None:
        """
        Ensure the parent directory of the authoritative index exists.
        Used by embeddings.py during publish.
        """
        cls.VECTOR_INDEX_DIR.parent.mkdir(parents=True, exist_ok=True)
