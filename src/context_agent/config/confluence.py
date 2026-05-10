"""
Configuration related to Confluence authentication and document export.
"""

from pathlib import Path
import os


class ConfluenceAuthConfig:
    """
    Configuration related to Confluence authentication and API access.
    Secrets are read from environment variables.
    """

    BASE_URL = os.getenv(
        "CONFLUENCE_BASE_URL",
        "https://<your org>.atlassian.net/wiki",
    )
    EMAIL = os.getenv("CONFLUENCE_EMAIL", "<your email id>")
    API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "<your access token>")


class ConfluenceDocsExportConfig:
    """
    Configuration specific to exporting Confluence pages as Markdown files.
    """
    PAGE_IDS = [
        "1078132894",
    ]

    # Resolve project root (…/src/context_agent/config → project root)
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    # Output directory for generated Markdown files
    OUTPUT_DIR = PROJECT_ROOT / "docs"
