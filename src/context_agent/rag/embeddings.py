import time
import json
import argparse
import shutil
from pathlib import Path
from typing import Any, Dict

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from context_agent.config.vectorization import VectorizationConfig
from context_agent.config.vector_index import VectorIndexConfig


# ----------------------------------------------------------------------
# CLI argument parsing
# ----------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Build and optionally publish vector index for ContextAgent"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help=(
            "Publish the validated vector index to the external "
            "authoritative location (only valid in STORAGE_MODE=external)"
        ),
    )
    return parser.parse_args()


# ----------------------------------------------------------------------
# Embeddings factory
# ----------------------------------------------------------------------
def create_embeddings():
    """
    Factory function to instantiate and return an embeddings backend
    based on VectorizationConfig.

    Backend + model MUST match between indexing and querying.
    """
    backend = VectorizationConfig.EMBEDDING_BACKEND
    model = VectorizationConfig.EMBEDDING_MODEL

    if backend == "sentence_transformers":
        if ":" in model:
            raise ValueError(
                f"Model '{model}' looks like an Ollama-style identifier. "
                "Sentence-transformers backend requires Hugging Face models."
            )

        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs={
                "device": VectorizationConfig.EMBEDDING_DEVICE
            },
        )

    elif backend == "ollama":
        if "/" in model:
            raise ValueError(
                f"Model '{model}' looks like a Hugging Face model. "
                "Ollama backend only supports Ollama-registered models."
            )

        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(
            model=model,
            num_thread=VectorizationConfig.EMBEDDING_NUM_THREADS,
        )

    else:
        raise ValueError(
            f"Unsupported EMBEDDING_BACKEND '{backend}'. "
            "Supported values are: 'sentence_transformers', 'ollama'."
        )


# ----------------------------------------------------------------------
# Validation helpers
# ----------------------------------------------------------------------
def validate_index(index_dir: Path) -> None:
    """
    Automated safety checks before publishing the index.

    Validates:
    - LangChain FAISS artifacts exist
    - FAISS index can be successfully loaded
    """
    required_files = [
        index_dir / "faiss.faiss",
        index_dir / "faiss.pkl",
        index_dir / "index_metadata.json",
    ]

    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        raise RuntimeError(
            "Vector index validation failed.\n"
            "Missing required files:\n"
            + "\n".join(missing)
        )

    # Deep validation: ensure FAISS index is loadable
    try:
        embeddings = create_embeddings()
        FAISS.load_local(
            folder_path=index_dir,
            embeddings=embeddings,
            index_name="faiss",
            allow_dangerous_deserialization=True,
        )
    except Exception as exc:
        raise RuntimeError(
            "FAISS index validation failed. Index could not be loaded."
        ) from exc


# ----------------------------------------------------------------------
# Publishing helper
# ----------------------------------------------------------------------
def publish_vector_index(build_dir: Path, publish_dir: Path) -> None:
    """
    Publish vector index to authoritative location (OneDrive / SharePoint safe).

    This function NEVER deletes the publish_dir itself.
    It only replaces its contents.
    """

    print("Publishing vector index:")
    print(f"  FROM: {build_dir}")
    print(f"  TO:   {publish_dir}")

    # Ensure directory exists (important if manually deleted)
    publish_dir.mkdir(parents=True, exist_ok=True)

    print("Cleaning existing index contents (OneDrive-safe)...")

    # Remove existing files
    for item in publish_dir.iterdir():
        try:
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)
        except PermissionError as exc:
            raise RuntimeError(
                f"Failed to remove existing file or directory: {item}\n"
                f"Make sure FastAPI is stopped and OneDrive is idle."
            ) from exc

    print("Copying new index files...")

    # Copy new artifacts
    for item in build_dir.iterdir():
        dest = publish_dir / item.name
        if item.is_file():
            shutil.copy2(item, dest)
        else:
            shutil.copytree(item, dest)

    print("Vector index published successfully.")

# ----------------------------------------------------------------------
# Vectorization pipeline
# ----------------------------------------------------------------------
def build_vector_index() -> None:
    """
    Load documents, split into chunks, generate embeddings,
    and build a FAISS index locally (non-authoritative).
    """
    build_dir = VectorIndexConfig.ensure_build_dir()

    # Prevent accidental overwrite
    if (build_dir / "index_metadata.json").exists():
        raise RuntimeError(
            "Local build directory already contains an index.\n"
            "Delete '.vector_build/vector_index' to rebuild."
        )

    print("Starting vector index build...")
    print(f"Source documents directory: {VectorizationConfig.DOCS_DIR}")

    # Load markdown documents
    loader = DirectoryLoader(
        path=str(VectorizationConfig.DOCS_DIR),
        glob=VectorizationConfig.DOCS_GLOB,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    t0 = time.perf_counter()
    documents = loader.load()
    print(f"Loaded {len(documents)} documents in {time.perf_counter() - t0:.2f}s")

    if not documents:
        raise RuntimeError(
            f"No documents found in {VectorizationConfig.DOCS_DIR}"
        )

    # Split documents into chunks (Chunking)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=VectorizationConfig.CHUNK_SIZE,
        chunk_overlap=VectorizationConfig.CHUNK_OVERLAP,
    )

    t1 = time.perf_counter()
    docs = splitter.split_documents(documents)
    print(
        f"Split into {len(docs)} chunks in {time.perf_counter() - t1:.2f}s"
    )

    if not docs:
        raise RuntimeError("Document splitting produced zero chunks")

    # Create embeddings & build FAISS index
    print(
        f"Starting embedding phase using backend '{VectorizationConfig.EMBEDDING_BACKEND}' "
        f"and model '{VectorizationConfig.EMBEDDING_MODEL}'.\n"
        "This may take some time depending on document size and hardware..."
    )

    embeddings = create_embeddings()

    t_embed = time.perf_counter()
    vectorstore = FAISS.from_documents(docs, embeddings)

    print(f"Embed + index time: {time.perf_counter() - t_embed:.2f}s")
    print(f"Chunks indexed: {vectorstore.index.ntotal}")
    print(f"Vector dimension: {vectorstore.index.d}")

    # Persist index + metadata
    metadata: Dict[str, Any] = {
        "embedding_backend": VectorizationConfig.EMBEDDING_BACKEND,
        "embedding_model": VectorizationConfig.EMBEDDING_MODEL,
        "chunk_size": VectorizationConfig.CHUNK_SIZE,
        "chunk_overlap": VectorizationConfig.CHUNK_OVERLAP,
        "vectorizer_version": "v1",
        "document_count": len(documents),
        "chunk_count": len(docs),
        "build_timestamp": int(time.time()),
    }

    t_save_index = time.perf_counter()
    vectorstore.save_local(
        folder_path=build_dir,
        index_name="faiss",
    )

    with (build_dir / "index_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(
        f"Local vector index written to: {build_dir} "
        f"in {time.perf_counter() - t_save_index:.2f}s"
    )


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def main():
    args = parse_args()

    build_vector_index()
    build_dir = VectorIndexConfig.VECTOR_INDEX_BUILD_DIR

    validate_index(build_dir)

    if args.publish:
        if VectorIndexConfig.STORAGE_MODE != "external":
            raise RuntimeError(
                "--publish is only valid when STORAGE_MODE=external"
            )

        publish_vector_index(
            build_dir,
            VectorIndexConfig.VECTOR_INDEX_PUBLISH_DIR,
        )

        print("Vector index published successfully.")
    else:
        print("Vector index built locally (not published).")


if __name__ == "__main__":
    main()
