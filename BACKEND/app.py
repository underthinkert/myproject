from fastapi import FastAPI, HTTPException

from models import (
    InterviewRequest,
    InterviewResponse,
)

from interview import (
    start_interview,
    continue_interview,
)


app = FastAPI(
    title="AI Interview Agent Backend",
    version="1.0.0",
)


@app.get("/")
def home():

    return {
        "message": "Welcome to AI Interview Agent Backend"
    }


@app.get("/health")
def health():

    return {
        "status": "Backend is running successfully"
    }


@app.post(
    "/api/interview",
    response_model=InterviewResponse,
)
def interview(
    request: InterviewRequest
):

    # Start interview
    if request.candidate is not None:

        return start_interview(
            request.sessionId,
            request.candidate,
        )

    # Continue interview
    if request.message is not None:

        if not request.message.strip():

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty.",
            )

        return continue_interview(
            request.sessionId,
            request.message,
        )

    raise HTTPException(
        status_code=400,
        detail="Provide either candidate or message.",
    )