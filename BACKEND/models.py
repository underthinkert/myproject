from typing import Any

from pydantic import BaseModel, Field


# ============================================================
# INTERVIEW FEEDBACK
# ============================================================

class InterviewFeedback(BaseModel):
    """
    Final structured feedback returned after the interview.
    """

    summary: str = ""

    strengths: list[str] = Field(
        default_factory=list
    )

    gaps: list[str] = Field(
        default_factory=list
    )

    next: list[str] = Field(
        default_factory=list
    )


# ============================================================
# INTERVIEW REQUEST
# ============================================================

class InterviewRequest(BaseModel):

    sessionId: str

    candidate: dict[str, Any] | None = None

    message: str | None = None


# ============================================================
# INTERVIEW RESPONSE
# ============================================================

class InterviewResponse(BaseModel):

    reply: str

    done: bool

    feedback: InterviewFeedback | None = None