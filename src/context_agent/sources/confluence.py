"""
Exports Confluence pages to Markdown files.

This module:
1. Fetches Confluence pages using the REST API
2. Extracts the page body in HTML format
3. Converts HTML to Markdown
4. Saves the content as .md files under the project's docs/ directory

Markdown filenames include the Confluence page ID to ensure
uniqueness and traceability.
"""

import re
import unicodedata
import requests
from markdownify import markdownify as md
from pathlib import Path

from context_agent.config.confluence import (
    ConfluenceAuthConfig,
    ConfluenceDocsExportConfig,
)


# ----------------------------------------------------------------------
# Filename sanitation
# ----------------------------------------------------------------------
def sanitize_filename(name: str) -> str:
    """
    Make a string safe for use as a Windows filename.
    """

    # Normalize Unicode (handles fancy quotes, accented chars, etc.)
    name = unicodedata.normalize("NFKD", name)

    # Remove forbidden Windows filename characters
    name = re.sub(r'[<>:"/\\|?*]', "", name)

    # Normalize dashes
    name = name.replace("–", "-").replace("—", "-")

    # Replace whitespace with underscores
    name = re.sub(r"\s+", "_", name.strip())

    # Collapse repeated underscores
    name = re.sub(r"_+", "_", name)

    return name


# ----------------------------------------------------------------------
# Confluence fetch
# ----------------------------------------------------------------------
def fetch_confluence_page(page_id: str) -> dict:
    """
    Fetch a Confluence page by its page ID.
    """
    url = (
        f"{ConfluenceAuthConfig.BASE_URL}"
        f"/rest/api/content/{page_id}?expand=body.storage"
    )

    response = requests.get(
        url,
        auth=(ConfluenceAuthConfig.EMAIL, ConfluenceAuthConfig.API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch page {page_id} (HTTP {response.status_code})"
        )

    return response.json()


# ----------------------------------------------------------------------
# Markdown export
# ----------------------------------------------------------------------
def save_page_as_markdown(
    page_id: str,
    title: str,
    html_content: str,
) -> Path:
    """
    Convert HTML content to Markdown and save it to a file.

    Filename format:
        <page_id>__<sanitized_title>.md

    Example:
        12345678__Incident_Response_Runbook.md
    """

    markdown_content = md(html_content)

    output_dir = ConfluenceDocsExportConfig.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Centralized, Windows-safe filename sanitation
    safe_title = sanitize_filename(title)

    filename = f"{page_id}__{safe_title}.md"
    file_path = output_dir / filename

    file_path.write_text(markdown_content, encoding="utf-8")
    return file_path


# ----------------------------------------------------------------------
# Export entry point
# ----------------------------------------------------------------------
def export_pages() -> None:
    """
    Export all configured Confluence pages as Markdown files.

    A failure in one page does not stop the others.
    """

    for page_id in ConfluenceDocsExportConfig.PAGE_IDS:
        try:
            page_data = fetch_confluence_page(page_id)

            title = page_data["title"]
            html_content = page_data["body"]["storage"]["value"]

            print(f"Fetched page: {title} (ID: {page_id})")

            file_path = save_page_as_markdown(
                page_id=page_id,
                title=title,
                html_content=html_content,
            )

            print(f"Saved to: {file_path}\n")

        except Exception as exc:
            print(f"Error processing page {page_id}: {exc}\n")


if __name__ == "__main__":
    export_pages()
