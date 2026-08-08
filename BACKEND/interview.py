import json
from pathlib import Path

from llm_client import generate_response

from memory import (
    create_session,
    get_session,
    add_exchange,
    get_recent_conversation,
    get_full_conversation,
    get_candidate_profile,
    increment_question,
    get_question_number,
    get_covered_topics,
    get_topic_question_counts,
    update_interview_state,
    get_evaluations,
    get_strengths,
    get_weaknesses,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_INTERVIEW_QUESTIONS = 8
MIN_CURRICULUM_TOPICS = 4

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
CURRICULUM_FILE = DATA_DIR / "curriculum.json"


# ============================================================
# JSON PARSER
# ============================================================

def parse_json_response(raw_response: str):

    if not raw_response:
        return None

    if not isinstance(raw_response, str):
        return None

    cleaned = raw_response.strip()

    if cleaned.startswith("```"):

        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    try:

        result = json.loads(cleaned)

        if isinstance(result, str):

            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                pass

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:

        try:

            result = json.loads(
                cleaned[start:end + 1]
            )

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    return None


# ============================================================
# STRING LIST
# ============================================================

def normalize_string_list(value):

    if not isinstance(value, list):
        return []

    result = []

    for item in value:

        if isinstance(item, str):

            item = item.strip()

            if item:
                result.append(item)

    return result


# ============================================================
# LOAD CURRICULUM
# ============================================================

def load_curriculum():

    if not CURRICULUM_FILE.exists():

        raise FileNotFoundError(
            f"Curriculum file not found: {CURRICULUM_FILE}"
        )

    with open(
        CURRICULUM_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        curriculum = json.load(f)

    if not isinstance(curriculum, dict):

        raise ValueError(
            "curriculum.json must contain a JSON object."
        )

    return curriculum


def get_curriculum_days(curriculum):

    days = curriculum.get("days", [])

    if not isinstance(days, list):
        return []

    return [
        item
        for item in days
        if isinstance(item, dict)
    ]


# ============================================================
# CANDIDATE TOPICS
# ============================================================

def get_candidate_topics(candidate):

    topics = []

    if not isinstance(candidate, dict):
        return topics

    missions = candidate.get("missions", [])

    if not isinstance(missions, list):
        return topics

    for mission in missions:

        if not isinstance(mission, dict):
            continue

        if mission.get("passed") is True:

            title = mission.get("title")

            if isinstance(title, str) and title.strip():
                topics.append(title.strip())

    return topics


# ============================================================
# CURRICULUM SUMMARY
# ============================================================

def build_curriculum_summary(curriculum):

    summary = []

    for item in get_curriculum_days(curriculum):

        summary.append({
            "day": item.get("day"),
            "title": item.get("title", ""),
            "tools": item.get("tools", []),
            "objectives": item.get("objectives", []),
        })

    return summary


# ============================================================
# QUESTION NORMALIZATION
# ============================================================

def normalize_question(question):

    if not isinstance(question, str):
        return ""

    return " ".join(
        question.lower().strip().split()
    )


# ============================================================
# GET PREVIOUS QUESTIONS
# ============================================================

def get_previous_questions(session_id):

    conversation = get_full_conversation(
        session_id
    )

    result = []

    for exchange in conversation:

        if not isinstance(exchange, dict):
            continue

        question = exchange.get(
            "question",
            ""
        )

        if isinstance(question, str):
            question = question.strip()

            if question:
                result.append(question)

    return result


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate_question(
    session_id,
    question
):

    normalized = normalize_question(
        question
    )

    if not normalized:
        return True

    previous = get_previous_questions(
        session_id
    )

    for old_question in previous:

        old_normalized = normalize_question(
            old_question
        )

        if normalized == old_normalized:
            return True

    return False


# ============================================================
# CHOOSE NEXT TOPIC
# ============================================================

def choose_topic_for_question(
    curriculum,
    covered_topics,
    topic_counts,
):

    days = get_curriculum_days(curriculum)

    if not days:
        return None

    # First cover at least 4 different topics.
    if len(covered_topics) < MIN_CURRICULUM_TOPICS:

        for item in days:

            title = item.get("title")

            if (
                title
                and title not in covered_topics
            ):
                return item

    # Then choose least-used topic.
    candidates = []

    for item in days:

        title = item.get("title")

        if not title:
            continue

        count = topic_counts.get(
            title,
            0
        )

        candidates.append(
            (
                count,
                item.get(
                    "day",
                    999999
                ),
                item
            )
        )

    candidates.sort(
        key=lambda x: (
            x[0],
            x[1]
        )
    )

    return (
        candidates[0][2]
        if candidates
        else None
    )


# ============================================================
# FALLBACK QUESTION
# ============================================================

def build_fallback_question(
    selected
):

    if not selected:
        return (
            "How would you validate a "
            "production system for reliability, "
            "security, and maintainability?"
        )

    objectives = selected.get(
        "objectives",
        []
    )

    if isinstance(objectives, list):

        for objective in objectives:

            if (
                isinstance(objective, str)
                and objective.strip()
            ):

                return (
                    "How would you approach "
                    + objective.strip()
                    + " in a production system?"
                )

    title = selected.get(
        "title",
        "this technical area"
    )

    return (
        "How would you design and validate "
        f"a production solution related to {title}?"
    )


# ============================================================
# FIRST QUESTION
# ============================================================

def build_first_question(candidate):

    curriculum = load_curriculum()

    member = candidate.get(
        "member",
        {}
    )

    if not isinstance(member, dict):
        member = {}

    name = member.get(
        "name",
        "Candidate"
    )

    role = member.get(
        "jobRole",
        "Software Engineer"
    )

    experience = member.get(
        "yearsExperience",
        0
    )

    education = member.get(
        "education",
        "Not specified"
    )

    completed_topics = get_candidate_topics(
        candidate
    )

    curriculum_summary = (
        build_curriculum_summary(
            curriculum
        )
    )

    prompt = f"""
You are a professional technical interviewer.

Candidate:
Name: {name}
Role: {role}
Years of experience: {experience}
Education: {education}

Previously demonstrated topics:
{json.dumps(completed_topics)}

Curriculum:
{json.dumps(curriculum_summary)}

This is QUESTION 1 of exactly 8.

Rules:

- Ask exactly ONE technical question.
- Do not number it.
- Do not provide an answer.
- Do not ask multiple questions.
- Match the candidate's experience.
- Ask a realistic engineering question.
- Return ONLY valid JSON.

Return:

{{
    "question": "one technical interview question",
    "day": 1,
    "topic": "curriculum topic"
}}
"""

    raw = generate_response(prompt)

    result = parse_json_response(raw)

    if isinstance(result, dict):

        question = result.get(
            "question"
        )

        if (
            isinstance(question, str)
            and question.strip()
        ):

            return {
                "question": question.strip(),
                "day": result.get("day"),
                "topic": result.get("topic"),
            }

    curriculum_days = get_curriculum_days(
        curriculum
    )

    if curriculum_days:

        first = curriculum_days[0]

        return {
            "question": build_fallback_question(
                first
            ),
            "day": first.get("day", 1),
            "topic": first.get(
                "title",
                "Technical Development"
            ),
        }

    return {
        "question": (
            "How would you design a reliable "
            "Python development environment "
            "for a production project?"
        ),
        "day": 1,
        "topic": "Python Development",
    }


# ============================================================
# START INTERVIEW
# ============================================================

def start_interview(
    session_id: str,
    candidate: dict,
):

    if not isinstance(candidate, dict):
        candidate = {}

    member = candidate.get(
        "member",
        {}
    )

    if not isinstance(member, dict):
        member = {}

    candidate_name = member.get(
        "name",
        "Candidate"
    )

    # Always create a fresh session.
    create_session(
        session_id=session_id,
        candidate_name=candidate_name,
        candidate_profile=candidate,
    )

    first = build_first_question(
        candidate
    )

    question = first.get(
        "question",
        "Tell me about your technical experience."
    )

    day = first.get("day")
    topic = first.get("topic")

    session = get_session(
        session_id
    )

    session["current_question"] = question
    session["current_question_day"] = day
    session["current_question_topic"] = topic

    update_interview_state(
        session_id=session_id,
        topic=topic,
        day=day,
        difficulty="medium",
    )

    return {
        "reply": (
            f"Welcome {candidate_name}. "
            f"{question}"
        ),
        "done": False,
        "feedback": None,
    }


# ============================================================
# FINAL REPORT
# ============================================================

def generate_final_feedback(
    session_id
):

    conversation = get_full_conversation(
        session_id
    )

    candidate = get_candidate_profile(
        session_id
    )

    evaluations = get_evaluations(
        session_id
    )

    stored_strengths = get_strengths(
        session_id
    )

    stored_gaps = get_weaknesses(
        session_id
    )

    covered_topics = get_covered_topics(
        session_id
    )

    member = candidate.get(
        "member",
        {}
    )

    if not isinstance(member, dict):
        member = {}

    candidate_name = member.get(
        "name",
        "Candidate"
    )

    role = member.get(
        "jobRole",
        "Software Engineer"
    )

    # Never generate final report early.
    if len(conversation) < MAX_INTERVIEW_QUESTIONS:

        return {
            "summary": (
                "Interview is not complete."
            ),
            "strengths": stored_strengths,
            "gaps": stored_gaps,
            "next": [
                "Complete all 8 questions."
            ],
        }

    conversation = conversation[
        :MAX_INTERVIEW_QUESTIONS
    ]

    prompt = f"""
You are a senior technical interviewer.

Generate the FINAL technical assessment.

Candidate:
Name: {candidate_name}
Role: {role}

Exactly 8 answers were collected.

Interview:

{json.dumps(conversation, indent=2)}

Evaluations:

{json.dumps(evaluations, indent=2)}

Topics:

{json.dumps(covered_topics, indent=2)}

Evaluate only what the candidate demonstrated.

Do not invent experience or skills.

Return ONLY valid JSON:

{{
    "summary": "overall technical assessment",
    "strengths": [
        "specific demonstrated strength"
    ],
    "gaps": [
        "specific demonstrated weakness"
    ],
    "next": [
        "specific actionable recommendation"
    ]
}}

No Markdown.
No extra keys.
"""

    raw = generate_response(
        prompt
    )

    feedback = parse_json_response(
        raw
    )

    if isinstance(feedback, dict):

        summary = feedback.get(
            "summary",
            ""
        )

        strengths = normalize_string_list(
            feedback.get(
                "strengths",
                []
            )
        )

        gaps = normalize_string_list(
            feedback.get(
                "gaps",
                []
            )
        )

        next_steps = normalize_string_list(
            feedback.get(
                "next",
                []
            )
        )

        if (
            isinstance(summary, str)
            and summary.strip()
        ):

            return {
                "summary": summary.strip(),
                "strengths": (
                    strengths
                    or stored_strengths
                ),
                "gaps": (
                    gaps
                    or stored_gaps
                ),
                "next": (
                    next_steps
                    or [
                        "Continue building production-grade projects."
                    ]
                ),
            }

    return {
        "summary": (
            f"{candidate_name} completed the "
            f"{MAX_INTERVIEW_QUESTIONS}-question "
            "technical interview."
        ),
        "strengths": (
            stored_strengths
            or [
                "Demonstrated technical understanding during the interview."
            ]
        ),
        "gaps": (
            stored_gaps
            or [
                "Continue developing deeper production-level expertise."
            ]
        ),
        "next": [
            "Practice production-oriented technical projects."
        ],
    }


# ============================================================
# CONTINUE INTERVIEW
# ============================================================

def continue_interview(
    session_id: str,
    candidate_answer: str,
):

    session = get_session(
        session_id
    )

    if not session:

        return {
            "reply": (
                "Interview session not found. "
                "Please start a new interview."
            ),
            "done": False,
            "feedback": None,
        }

    # --------------------------------------------------------
    # Validate answer
    # --------------------------------------------------------

    if not isinstance(
        candidate_answer,
        str
    ):

        candidate_answer = str(
            candidate_answer or ""
        )

    candidate_answer = (
        candidate_answer.strip()
    )

    if not candidate_answer:

        return {
            "reply": (
                "Please provide an answer "
                "before continuing."
            ),
            "done": False,
            "feedback": None,
        }

    # --------------------------------------------------------
    # Number of answers already received
    # --------------------------------------------------------

    answered_count = get_question_number(
        session_id
    )

    # --------------------------------------------------------
    # HARD STOP
    #
    # If 8 answers already exist, NEVER call LLM again.
    # --------------------------------------------------------

    if answered_count >= MAX_INTERVIEW_QUESTIONS:

        final_feedback = (
            generate_final_feedback(
                session_id
            )
        )

        return {
            "reply": "Interview completed.",
            "done": True,
            "feedback": final_feedback,
        }

    # --------------------------------------------------------
    # Current question
    # --------------------------------------------------------

    current_question = session.get(
        "current_question"
    )

    current_topic = session.get(
        "current_question_topic"
    )

    current_day = session.get(
        "current_question_day"
    )

    if not current_question:

        current_question = (
            "Tell me about your technical experience."
        )

    # --------------------------------------------------------
    # Current question number
    # --------------------------------------------------------

    current_question_number = (
        answered_count + 1
    )

    is_final_answer = (
        current_question_number
        == MAX_INTERVIEW_QUESTIONS
    )

    # --------------------------------------------------------
    # Candidate
    # --------------------------------------------------------

    candidate = get_candidate_profile(
        session_id
    )

    member = candidate.get(
        "member",
        {}
    )

    if not isinstance(member, dict):
        member = {}

    candidate_name = member.get(
        "name",
        "Candidate"
    )

    role = member.get(
        "jobRole",
        "Software Engineer"
    )

    experience = member.get(
        "yearsExperience",
        0
    )

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    curriculum = load_curriculum()

    curriculum_summary = (
        build_curriculum_summary(
            curriculum
        )
    )

    covered_topics = get_covered_topics(
        session_id
    )

    topic_counts = (
        get_topic_question_counts(
            session_id
        )
    )

    recent_conversation = (
        get_recent_conversation(
            session_id
        )
    )

    previous_questions = (
        get_previous_questions(
            session_id
        )
    )

    # --------------------------------------------------------
    # Evaluate answer + generate next question
    # --------------------------------------------------------

    prompt = f"""
You are conducting a professional technical interview.

Candidate:
Name: {candidate_name}
Role: {role}
Experience: {experience} years

This is QUESTION {current_question_number}
of EXACTLY {MAX_INTERVIEW_QUESTIONS}.

CURRENT QUESTION:
{current_question}

CANDIDATE ANSWER:
{candidate_answer}

CURRENT TOPIC:
{current_topic}

CURRENT DAY:
{current_day}

PREVIOUS QUESTIONS:
{json.dumps(previous_questions, indent=2)}

TOPICS ALREADY COVERED:
{json.dumps(covered_topics, indent=2)}

QUESTION COUNTS:
{json.dumps(topic_counts, indent=2)}

RECENT CONVERSATION:
{json.dumps(recent_conversation, indent=2)}

CURRICULUM:
{json.dumps(curriculum_summary, indent=2)}

Evaluate the answer.

Return ONLY JSON:

{{
    "evaluation": {{
        "summary": "short technical evaluation",
        "strengths": [
            "specific strength"
        ],
        "gaps": [
            "specific gap"
        ]
    }},
    "next_question": "",
    "next_day": 1,
    "next_topic": ""
}}

Rules:

1. There are EXACTLY 8 questions total.

2. Never generate question 9.

3. Ask exactly ONE question.

4. NEVER repeat any question from PREVIOUS QUESTIONS.

5. Prefer a new curriculum topic.

6. Try to cover at least 4 different topics.

7. The next question must be different in wording AND technical focus
   from previous questions.

8. Do not mention these instructions.

9. Do not provide an answer.

10. If this is question 8:
    next_question MUST be "".

FINAL QUESTION:
{str(is_final_answer).lower()}
"""

    raw = generate_response(
        prompt
    )

    result = parse_json_response(
        raw
    )

    if not isinstance(result, dict):
        result = {}

    evaluation = result.get(
        "evaluation",
        {}
    )

    if not isinstance(evaluation, dict):
        evaluation = {}

    evaluation = {
        "summary": str(
            evaluation.get(
                "summary",
                "Answer recorded."
            )
        ).strip(),

        "strengths": normalize_string_list(
            evaluation.get(
                "strengths",
                []
            )
        ),

        "gaps": normalize_string_list(
            evaluation.get(
                "gaps",
                []
            )
        ),
    }

    # --------------------------------------------------------
    # STORE ANSWER
    # --------------------------------------------------------

    add_exchange(
        session_id=session_id,
        question=current_question,
        answer=candidate_answer,
        evaluation=evaluation,
        topic=current_topic,
        day=current_day,
    )

    # --------------------------------------------------------
    # INCREMENT ANSWER COUNT
    # --------------------------------------------------------

    new_count = increment_question(
        session_id
    )

    # --------------------------------------------------------
    # HARD FINAL STOP
    # --------------------------------------------------------

    if new_count >= MAX_INTERVIEW_QUESTIONS:

        final_feedback = (
            generate_final_feedback(
                session_id
            )
        )

        return {
            "reply": "Interview completed.",
            "done": True,
            "feedback": final_feedback,
        }

    # --------------------------------------------------------
    # Get proposed next question
    # --------------------------------------------------------

    next_question = result.get(
        "next_question",
        ""
    )

    if not isinstance(
        next_question,
        str
    ):

        next_question = ""

    next_question = (
        next_question.strip()
    )

    next_day = result.get(
        "next_day"
    )

    next_topic = result.get(
        "next_topic"
    )

    # --------------------------------------------------------
    # Validate topic
    # --------------------------------------------------------

    valid_topics = {
        item.get("title"): item
        for item in get_curriculum_days(
            curriculum
        )
        if item.get("title")
    }

    if next_topic not in valid_topics:

        selected = (
            choose_topic_for_question(
                curriculum,
                covered_topics,
                topic_counts,
            )
        )

        if selected:

            next_topic = selected.get(
                "title"
            )

            next_day = selected.get(
                "day"
            )

    # --------------------------------------------------------
    # DUPLICATE QUESTION PROTECTION
    # --------------------------------------------------------

    if (
        not next_question
        or is_duplicate_question(
            session_id,
            next_question
        )
    ):

        selected = valid_topics.get(
            next_topic
        )

        if not selected:

            selected = (
                choose_topic_for_question(
                    curriculum,
                    covered_topics,
                    topic_counts,
                )
            )

        # Try several topics until a non-duplicate
        # fallback question is found.

        candidate_questions = []

        if selected:

            candidate_questions.append(
                (
                    selected,
                    build_fallback_question(
                        selected
                    )
                )
            )

        for item in get_curriculum_days(
            curriculum
        ):

            candidate_questions.append(
                (
                    item,
                    build_fallback_question(
                        item
                    )
                )
            )

        found = False

        for item, question in candidate_questions:

            if not is_duplicate_question(
                session_id,
                question
            ):

                selected = item
                next_question = question
                next_topic = item.get(
                    "title"
                )
                next_day = item.get(
                    "day"
                )

                found = True
                break

        if not found:

            # Extremely safe unique fallback.
            next_question = (
                "How would you validate the "
                "reliability, security, scalability, "
                "and maintainability of a production "
                "system you have designed?"
            )

            next_topic = (
                "Production Engineering"
            )

            next_day = 999

    # --------------------------------------------------------
    # FINAL duplicate safety check
    # --------------------------------------------------------

    if is_duplicate_question(
        session_id,
        next_question
    ):

        next_question = (
            "How would you identify and resolve "
            "the most important reliability risks "
            "in a production software system?"
        )

    # --------------------------------------------------------
    # Store next question
    # --------------------------------------------------------

    session["current_question"] = (
        next_question
    )

    session["current_question_day"] = (
        next_day
    )

    session["current_question_topic"] = (
        next_topic
    )

    update_interview_state(
        session_id=session_id,
        topic=next_topic,
        day=next_day,
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "reply": next_question,
        "done": False,
        "feedback": None,
    }