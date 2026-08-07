import json
from pathlib import Path

from llm_client import generate_response

from memory import (
    create_session,
    get_session,
    add_exchange,
    get_recent_conversation,
    get_candidate_profile,
    increment_question,
    get_question_number,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_INTERVIEW_QUESTIONS = 8

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"

CURRICULUM_FILE = DATA_DIR / "curriculum.json"


# ============================================================
# LOAD CURRICULUM
# ============================================================

def load_curriculum():
    with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# CANDIDATE TOPICS
# ============================================================

def get_candidate_topics(candidate):
    topics = []

    for mission in candidate.get("missions", []):
        if mission.get("passed") is True:
            title = mission.get("title")

            if title:
                topics.append(title)

    return topics


# ============================================================
# BUILD FIRST QUESTION
# ============================================================

def build_first_question(candidate):
    curriculum = load_curriculum()

    member = candidate.get("member", {})

    name = member.get("name", "Candidate")
    role = member.get("jobRole", "Software Engineer")
    experience = member.get("yearsExperience", 0)
    education = member.get("education", "Not specified")

    completed_topics = get_candidate_topics(candidate)

    prompt = f"""
You are a professional technical interviewer conducting
an AI/Software Engineering interview.

Candidate profile:

Name: {name}
Role: {role}
Years of experience: {experience}
Education: {education}

Topics the candidate has demonstrated experience with:

{json.dumps(completed_topics, indent=2)}

The candidate's learning curriculum is:

{json.dumps(curriculum.get("modules", []), indent=2)}

Generate the FIRST technical interview question.

Requirements:

- Make it appropriate for the candidate's experience level.
- Use their role and demonstrated technical background.
- Do not ask a basic question to an experienced candidate.
- Prefer a practical, scenario-based technical question.
- Ask exactly ONE question.
- Do not provide the answer.
- Do not ask multiple questions.

Return ONLY the interview question.
"""

    return generate_response(prompt).strip()


# ============================================================
# START INTERVIEW
# ============================================================

def start_interview(session_id: str, candidate: dict):

    member = candidate.get("member", {})
    candidate_name = member.get("name", "Candidate")

    create_session(
        session_id=session_id,
        candidate_name=candidate_name,
        candidate_profile=candidate
    )

    question = build_first_question(candidate)

    return {
        "reply": f"Welcome {candidate_name}. {question}",
        "done": False,
        "feedback": None
    }


# ============================================================
# FINAL FEEDBACK
# ============================================================

def generate_final_feedback(session_id: str):

    candidate = get_candidate_profile(session_id)
    conversation = get_recent_conversation(session_id)

    member = candidate.get("member", {})

    candidate_name = member.get("name", "Candidate")
    role = member.get("jobRole", "Software Engineer")
    experience = member.get("yearsExperience", 0)

    prompt = f"""
You are a senior technical interviewer.

Generate final technical interview feedback.

Candidate:

Name: {candidate_name}
Role: {role}
Years of experience: {experience}

Complete interview conversation:

{json.dumps(conversation, indent=2)}

Evaluate the candidate based ONLY on their actual answers.

Return JSON in EXACTLY this format:

{{
    "summary": "Overall assessment of the candidate.",
    "strengths": [
        "specific strength demonstrated by the candidate"
    ],
    "gaps": [
        "specific technical weakness or missing concept"
    ],
    "next": [
        "specific actionable recommendation"
    ]
}}

Requirements:

- Do NOT mention user safety.
- Do NOT return generic text.
- Do NOT invent skills that the candidate did not demonstrate.
- Base strengths on actual answers.
- Base gaps on actual weaknesses.
- Give technically meaningful feedback.
- Recommendations must be actionable.
- Keep each item concise.
- Return ONLY valid JSON.
"""

    raw_response = generate_response(prompt).strip()

    try:
        feedback = json.loads(raw_response)

    except json.JSONDecodeError:

        feedback = {
            "summary": (
                "The interview was completed, but the "
                "feedback response could not be parsed."
            ),
            "strengths": [],
            "gaps": [],
            "next": []
        }

    return {
        "summary": str(
            feedback.get(
                "summary",
                "Interview completed."
            )
        ),
        "strengths": feedback.get("strengths", []),
        "gaps": feedback.get("gaps", []),
        "next": feedback.get("next", [])
    }


# ============================================================
# CONTINUE INTERVIEW
# ============================================================

def continue_interview(
    session_id: str,
    candidate_answer: str
):

    # --------------------------------------------------------
    # 1. Find existing session
    # --------------------------------------------------------

    session = get_session(session_id)

    if not session:
        return {
            "reply": (
                "Interview session not found. "
                "Please start a new interview."
            ),
            "done": False,
            "feedback": None
        }

    # --------------------------------------------------------
    # 2. Get candidate information
    # --------------------------------------------------------

    candidate = get_candidate_profile(session_id)

    recent_conversation = get_recent_conversation(session_id)

    candidate_member = candidate.get("member", {})

    candidate_name = candidate_member.get(
        "name",
        "Candidate"
    )

    role = candidate_member.get(
        "jobRole",
        "Software Engineer"
    )

    experience = candidate_member.get(
        "yearsExperience",
        0
    )

    # --------------------------------------------------------
    # 3. Get previous question
    # --------------------------------------------------------

    if recent_conversation:
        previous_question = (
            recent_conversation[-1]["question"]
        )
    else:
        previous_question = (
            "The initial interview question."
        )

    # --------------------------------------------------------
    # 4. Evaluate answer and generate next question
    # --------------------------------------------------------

    prompt = f"""
You are conducting a professional technical interview.

Candidate:

Name: {candidate_name}
Role: {role}
Years of experience: {experience}

Previous interview question:

{previous_question}

Candidate's latest answer:

{candidate_answer}

Recent interview history:

{json.dumps(recent_conversation, indent=2)}

Evaluate the candidate's latest answer.

Consider:

- Technical correctness
- Depth of understanding
- Practical experience
- Architecture and design thinking
- Scalability
- Reliability
- Important missing concepts

Then generate ONE appropriate follow-up
technical interview question.

The next question must:

- Build naturally on the candidate's answer.
- Not repeat a previous question.
- Match the candidate's experience level.
- Probe deeper where appropriate.
- Be practical and scenario-based where possible.
- Ask exactly ONE question.

Return JSON in EXACTLY this format:

{{
    "evaluation": {{
        "summary": "short technical evaluation",
        "strengths": [
            "specific demonstrated strength"
        ],
        "gaps": [
            "specific missing concept or weakness"
        ]
    }},
    "next_question": "one technical interview question"
}}

Return ONLY valid JSON.
"""

    raw_response = generate_response(prompt).strip()

    # --------------------------------------------------------
    # 5. Parse LLM response
    # --------------------------------------------------------

    try:

        result = json.loads(raw_response)

    except json.JSONDecodeError:

        result = {
            "evaluation": {
                "summary": (
                    "The answer was reviewed, "
                    "but structured evaluation failed."
                ),
                "strengths": [],
                "gaps": []
            },
            "next_question": (
                "Can you explain how you would "
                "validate this architecture in production?"
            )
        }

    evaluation = result.get(
        "evaluation",
        {}
    )

    next_question = result.get(
        "next_question",
        "Can you explain your approach in more detail?"
    )

    # --------------------------------------------------------
    # 6. Store this question + answer + evaluation
    # --------------------------------------------------------

    add_exchange(
        session_id=session_id,
        question=previous_question,
        answer=candidate_answer,
        evaluation=evaluation
    )

    # --------------------------------------------------------
    # 7. Increment question counter
    # --------------------------------------------------------

    increment_question(session_id)

    # IMPORTANT:
    # Read the question number AFTER incrementing.
    question_number = get_question_number(session_id)

    # --------------------------------------------------------
    # 8. End interview after question 8
    # --------------------------------------------------------

    if question_number >= MAX_INTERVIEW_QUESTIONS:

        final_feedback = generate_final_feedback(
            session_id
        )

        return {
            "reply": "Interview completed.",
            "done": True,
            "feedback": final_feedback
        }

    # --------------------------------------------------------
    # 9. Continue interview
    # --------------------------------------------------------

    return {
        "reply": next_question,
        "done": False,
        "feedback": None
    }