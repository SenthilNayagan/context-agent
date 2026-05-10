import time
import json
from typing import Any, Dict, List
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from context_agent.config.vector_index import VectorIndexConfig
from context_agent.config.rag_query import RagQueryConfig
from context_agent.config.ollama import OllamaConfig


# ----------------------------------------------------------------------
# Embeddings factory (query-time)
# ----------------------------------------------------------------------
def create_embeddings_from_metadata(metadata: Dict[str, Any]):
    """
    Create embeddings based on index metadata.

    Guarantees query-time embeddings match indexing-time embeddings.
    """
    backend = metadata["embedding_backend"]
    model = metadata["embedding_model"]

    if backend == "sentence_transformers":
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model)

    elif backend == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=model)

    else:
        raise RuntimeError(
            f"Unsupported embedding backend in index metadata: {backend}"
        )


# ----------------------------------------------------------------------
# Vector index loader (cached)
# ----------------------------------------------------------------------
_VECTORSTORE_CACHE: FAISS | None = None


def load_vectorstore() -> FAISS:
    """
    Load and cache the authoritative FAISS vector index.
    """
    global _VECTORSTORE_CACHE

    if _VECTORSTORE_CACHE is not None:
        return _VECTORSTORE_CACHE

    index_dir: Path = VectorIndexConfig.VECTOR_INDEX_DIR

    required_files = [
        index_dir / "faiss.faiss",
        index_dir / "faiss.pkl",
        index_dir / "index_metadata.json",
    ]

    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        raise RuntimeError(
            "Vector index not found or incomplete.\n\n"
            f"Storage mode: {VectorIndexConfig.STORAGE_MODE}\n"
            f"Expected location:\n  {index_dir}\n\n"
            "Missing files:\n"
            + "\n".join(missing)
            + "\n\n"
            "If STORAGE_MODE=external:\n"
            "- Ensure the OneDrive-synced folder is available locally.\n"
            "If STORAGE_MODE=local:\n"
            "- Ensure embeddings have been generated in ./vector_index."
        )

    with (index_dir / "index_metadata.json").open("r", encoding="utf-8") as f:
        index_metadata = json.load(f)

    expected_version = "v1"
    if index_metadata.get("vectorizer_version") != expected_version:
        raise RuntimeError(
            "Vectorizer version mismatch "
            f"(expected {expected_version}, "
            f"found {index_metadata.get('vectorizer_version')})."
        )

    embeddings = create_embeddings_from_metadata(index_metadata)

    print(
        f"Loading vector index from:\n  {index_dir}\n"
        f"Storage mode: {VectorIndexConfig.STORAGE_MODE}"
    )

    _VECTORSTORE_CACHE = FAISS.load_local(
        folder_path=index_dir,
        embeddings=embeddings,
        index_name="faiss",
        allow_dangerous_deserialization=True,
    )

    return _VECTORSTORE_CACHE


# ----------------------------------------------------------------------
# Canonical RAG query function (REUSABLE)
# ----------------------------------------------------------------------
def run_query(question: str) -> Dict[str, Any]:
    """
    Execute a single RAG query and return structured results.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    vectorstore = load_vectorstore()
    ollama_cfg = OllamaConfig()

    # Similarity search
    docs = vectorstore.similarity_search(
        question,
        k=RagQueryConfig.TOP_K,
    )

    if not docs:
        if RagQueryConfig.FAIL_ON_EMPTY_CONTEXT:
            raise RuntimeError("No relevant documents retrieved.")
        context = ""
    else:
        context = "\n\n".join(doc.page_content for doc in docs)

    # Initialize LLM
    llm = OllamaLLM(
        model=ollama_cfg.model,
        temperature=ollama_cfg.temperature,
        base_url=ollama_cfg.base_url,
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You are an internal documentation assistant.

        Answer the question using ONLY the provided context.
        Explain clearly in your own words.
        If the context is insufficient, say so.

        Context:
        {context}

        Question:
        {question}
        """
    )

    response = llm.invoke(
        prompt.format_prompt(
            context=context,
            question=question,
        )
    )

    sources = list(
        dict.fromkeys(
            Path(doc.metadata["source"]).name
            for doc in docs
            if doc.metadata.get("source")
        )
    )

    return {
        "answer": str(response),
        "sources": sources,
    }


# ----------------------------------------------------------------------
# Interactive CLI loop
# ----------------------------------------------------------------------
def run_rag_query_loop() -> None:
    """
    Interactive RAG-based query loop over indexed documents.
    """
    print("RAG ready. Ask questions about your documents.")
    print("Type 'exit' to quit.")

    while True:
        query = input("\nQuestion: ").strip()
        if query.lower() == "exit":
            break

        t0 = time.perf_counter()

        try:
            result = run_query(query)
        except Exception as exc:
            print(f"\nError: {exc}")
            continue

        print("\nAnswer:")
        print(result["answer"])
        print(f"\nElapsed time: {time.perf_counter() - t0:.2f} seconds")


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    run_rag_query_loop()
