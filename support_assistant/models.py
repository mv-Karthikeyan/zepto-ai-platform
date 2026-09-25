# ============================================================
# ZEPTO SUPPORT ASSISTANT - PYDANTIC MODELS
# ============================================================

from typing import List

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """
    Request body accepted by the FastAPI /ask endpoint.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="User question"
    )


class AskResponse(BaseModel):
    """
    Final structured response returned by the assistant.
    """

    answer: str

    sources: List[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )