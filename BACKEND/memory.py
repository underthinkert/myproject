from collections import deque

MAX_RECENT_MEMORY = 5

interview_sessions = {}


def create_session(
    session_id: str,
    candidate_name: str,
    candidate_profile: dict | None = None
):
    interview_sessions[session_id] = {
        "candidate_name": candidate_name,
        "candidate_profile": candidate_profile or {},

        "recent_conversation": deque(
            maxlen=MAX_RECENT_MEMORY
        ),

        "all_conversation": [],

        # Number of answers already received.
        # 0 = Q1 waiting for answer
        # 7 = Q8 waiting for answer
        # 8 = interview completed
        "question_number": 0,

        "current_question": None,
        "current_question_day": None,
        "current_question_topic": None,

        "current_topic": None,
        "current_day": None,

        "covered_topics": [],
        "topic_question_counts": {},

        "difficulty": "medium",

        "evaluations": [],
        "strengths": [],
        "weaknesses": [],
    }


def get_session(session_id: str):
    return interview_sessions.get(session_id)


def add_exchange(
    session_id: str,
    question: str,
    answer: str,
    evaluation=None,
    topic=None,
    day=None
):
    session = interview_sessions.get(session_id)

    if not session:
        return

    exchange = {
        "question": question,
        "answer": answer,
        "evaluation": evaluation or {},
        "topic": topic,
        "day": day,
    }

    session["recent_conversation"].append(exchange)
    session["all_conversation"].append(exchange)

    if topic:
        if topic not in session["covered_topics"]:
            session["covered_topics"].append(topic)

        counts = session["topic_question_counts"]

        counts[topic] = counts.get(topic, 0) + 1

        session["current_topic"] = topic

    if day is not None:
        session["current_day"] = day

    if isinstance(evaluation, dict):

        session["evaluations"].append(evaluation)

        strengths = evaluation.get("strengths", [])

        if isinstance(strengths, list):
            for strength in strengths:
                if (
                    isinstance(strength, str)
                    and strength.strip()
                    and strength.strip()
                    not in session["strengths"]
                ):
                    session["strengths"].append(
                        strength.strip()
                    )

        gaps = evaluation.get("gaps", [])

        if isinstance(gaps, list):
            for gap in gaps:
                if (
                    isinstance(gap, str)
                    and gap.strip()
                    and gap.strip()
                    not in session["weaknesses"]
                ):
                    session["weaknesses"].append(
                        gap.strip()
                    )


def get_recent_conversation(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session["recent_conversation"]
    )


def get_full_conversation(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session["all_conversation"]
    )


def get_candidate_profile(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return {}

    return session.get(
        "candidate_profile",
        {}
    )


def update_interview_state(
    session_id: str,
    topic=None,
    difficulty=None,
    day=None
):

    session = interview_sessions.get(session_id)

    if not session:
        return

    if topic is not None:
        session["current_topic"] = topic

    if difficulty is not None:
        session["difficulty"] = difficulty

    if day is not None:
        session["current_day"] = day


def increment_question(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return 0

    session["question_number"] += 1

    return session["question_number"]


def get_question_number(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return 0

    return session.get(
        "question_number",
        0
    )


def get_covered_topics(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session.get(
            "covered_topics",
            []
        )
    )


def get_topic_question_counts(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return {}

    return dict(
        session.get(
            "topic_question_counts",
            {}
        )
    )


def get_evaluations(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session.get(
            "evaluations",
            []
        )
    )


def get_strengths(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session.get(
            "strengths",
            []
        )
    )


def get_weaknesses(session_id: str):

    session = interview_sessions.get(session_id)

    if not session:
        return []

    return list(
        session.get(
            "weaknesses",
            []
        )
    )


def delete_session(session_id: str):

    if session_id in interview_sessions:
        del interview_sessions[session_id]