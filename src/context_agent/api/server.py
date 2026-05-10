"""
FastAPI server for ContextAgent.

This module provides a thin HTTP interface over the existing
ContextAgent RAG pipeline. It is intentionally lightweight and
acts only as an adapter—no core logic lives here.

Run via:
    python -m context_agent.api.server
"""

import time
from typing import List

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ------------------------------------------------------------------
# Import existing RAG functionality (NO logic duplication)
# ------------------------------------------------------------------
from context_agent.rag import retriever


# ------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------
app = FastAPI(
    title="ContextAgent API",
    description="Local-first API for querying private knowledge bases",
    version="0.1.0",
)

# ------------------------------------------------------------------
# CORS configuration
#
# Required to allow browser-based UIs (e.g. local HTML files or
# localhost web frontends) to call this API via fetch().
#
# This is intentionally permissive for local development.
# In production or restricted environments, this should be
# tightened to specific allowed origins (e.g. http://localhost:3000).
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Development-only: allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow POST, OPTIONS (preflight), etc.
    allow_headers=["*"],          # Allow JSON content-type headers
)

# ------------------------------------------------------------------
# Request / Response models
# ------------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    elapsed_seconds: float


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# ------------------------------------------------------------------
# Root endpoint
# ------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "ContextAgent API is running",
        "docs": "http://127.0.0.1:8000/docs"
    }

# ------------------------------------------------------------------
# Query endpoint
# ------------------------------------------------------------------
@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    """
    Query the ContextAgent knowledge base.

    This endpoint:
    - Accepts a user question
    - Delegates to the existing retriever
    - Returns the answer with metadata
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start = time.perf_counter()

    try:
        # IMPORTANT:
        # This call should reuse existing logic.
        # Replace `run_query` with your actual retriever function.
        result = retriever.run_query(request.question)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {exc}",
        )

    elapsed = round(time.perf_counter() - start, 3)

    return QueryResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        elapsed_seconds=elapsed,
    )


# ------------------------------------------------------------------
# Local development entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "context_agent.api.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
