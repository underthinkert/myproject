from collections import deque


# ============================================================
# CONFIGURATION
# ============================================================

MAX_RECENT_MEMORY = 5


# ============================================================
# ACTIVE INTERVIEW SESSIONS
# ============================================================

interview_sessions = {}


# ============================================================
# CREATE SESSION
# ============================================================

def create_session(
    session_id: str,
    candidate_name: str,
    candidate_profile: dict | None = None
):
    interview_sessions[session_id] = {
        "candidate_name": candidate_name,

        # Candidate's permanent/core information
        "candidate_profile": candidate_profile or {},

        # Recent conversation memory
        "recent_conversation": deque(
            maxlen=MAX_RECENT_MEMORY
        ),

        # Number of candidate answers/questions completed
        # Starts at 0 because no question has been answered yet.
        "question_number": 0,

        # Interview state
        "current_topic": None,
        "difficulty": "medium",

        # Overall interview observations
        "evaluations": [],
        "strengths": [],
        "weaknesses": [],
    }


# ============================================================
# GET SESSION
# ============================================================

def get_session(session_id: str):
    return interview_sessions.get(session_id)


# ============================================================
# ADD QUESTION + ANSWER + EVALUATION
# ============================================================

def add_exchange(
    session_id: str,
    question: str,
    answer: str,
    evaluation=None
):
    session = interview_sessions.get(session_id)

    if not session:
        return

    session["recent_conversation"].append({
        "question": question,
        "answer": answer,
        "evaluation": evaluation
    })

    # Store evaluation
    if evaluation:

        session["evaluations"].append(evaluation)

        # Keep unique strengths
        for strength in evaluation.get(
            "strengths",
            []
        ):
            if strength not in session["strengths"]:
                session["strengths"].append(strength)

        # Keep unique weaknesses/gaps
        for gap in evaluation.get(
            "gaps",
            []
        ):
            if gap not in session["weaknesses"]:
                session["weaknesses"].append(gap)


# ============================================================
# GET RECENT CONVERSATION
# ============================================================

def get_recent_conversation(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session["recent_conversation"]
    )


# ============================================================
# GET CANDIDATE PROFILE
# ============================================================

def get_candidate_profile(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return {}

    return session["candidate_profile"]


# ============================================================
# UPDATE INTERVIEW STATE
# ============================================================

def update_interview_state(
    session_id: str,
    topic=None,
    difficulty=None
):

    session = interview_sessions.get(session_id)

    if not session:
        return

    if topic is not None:
        session["current_topic"] = topic

    if difficulty is not None:
        session["difficulty"] = difficulty


# ============================================================
# INCREMENT QUESTION NUMBER
# ============================================================

def increment_question(session_id: str):

    session = interview_sessions.get(session_id)

    if session:
        session["question_number"] += 1


# ============================================================
# GET QUESTION NUMBER
# ============================================================

def get_question_number(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return 0

    return session["question_number"]