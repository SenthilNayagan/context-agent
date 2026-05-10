"""
Configuration for Ollama LLM runtime.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OllamaConfig:
    """
    Configuration for Ollama inference engine.
    """

    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.0"))
    timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT", "2"))
