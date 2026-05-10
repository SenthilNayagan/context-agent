
"""
Main entry point for ContextAgent.

This module provides a single, canonical startup path for the application.

It is responsible for:
- Validating runtime prerequisites (e.g., Ollama availability)
- Handing off control to the RAG retriever loop

Run via:
    python -m context_agent
"""


from context_agent.rag.retriever import run_rag_query_loop
from context_agent.config.ollama import OllamaConfig

import requests


def check_ollama(config: OllamaConfig) -> None:
    """
    Validate that the Ollama server is running and the required model exists.
    Fail fast with a clear error message if not.
    """
    try:
        resp = requests.get(
            f"{config.base_url}/api/tags",
            timeout=config.timeout_seconds,
        )
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(
            "Ollama is not running or not reachable. "
            "Please start Ollama before running M1 OpsAgent."
        ) from exc

    models = {m["name"] for m in resp.json().get("models", [])}
    if config.model not in models:
        raise RuntimeError(
            f"Required Ollama model '{config.model}' not found. "
            f"Run: ollama pull {config.model}"
        )


def main() -> None:
    """
    Application entry point.
    """
    ollama_config = OllamaConfig()

    # Ensure Ollama is ready before starting the agent
    check_ollama(ollama_config)

    # Start interactive RAG loop
    run_rag_query_loop()


if __name__ == "__main__":
    main()
