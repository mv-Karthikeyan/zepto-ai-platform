# ============================================================
# ZEPTO SUPPORT ASSISTANT - FASTAPI APPLICATION
# ============================================================

from fastapi import FastAPI, HTTPException

from .graph import graph
from .models import AskRequest, AskResponse


app = FastAPI(
    title="Zepto Support Assistant",
    description=(
        "RAG-based Zepto policy support assistant using "
        "Sentence Transformers, ChromaDB and LangGraph."
    ),
    version="1.0.0"
)


@app.get("/")
def root():
    """
    Health-check endpoint.
    """
    return {
        "message": "Zepto Support Assistant API is running."
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    Send a question through the LangGraph workflow.
    """

    try:
        result = graph.invoke(
            {
                "query": request.query
            }
        )

        return AskResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence=result["confidence"]
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process the request: {str(exc)}"
        )