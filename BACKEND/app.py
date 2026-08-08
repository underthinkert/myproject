from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    InterviewRequest,
    InterviewResponse
)

from interview import (
    start_interview,
    continue_interview
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Interview Agent Backend",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Interview Agent Backend"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "Backend is running successfully"
    }


# ============================================================
# INTERVIEW ENDPOINT
# ============================================================

@app.post(
    "/api/interview",
    response_model=InterviewResponse
)
def interview(
    request: InterviewRequest
):

    # --------------------------------------------------------
    # START INTERVIEW
    # --------------------------------------------------------

    if request.candidate is not None:

        return start_interview(
            request.sessionId,
            request.candidate
        )

    # --------------------------------------------------------
    # CONTINUE INTERVIEW
    # --------------------------------------------------------

    if request.message is not None:

        if not request.message.strip():

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        return continue_interview(
            request.sessionId,
            request.message
        )

    # --------------------------------------------------------
    # INVALID REQUEST
    # --------------------------------------------------------

    raise HTTPException(
        status_code=400,
        detail="Provide either candidate or message."
    )