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

# We want the interview to touch at least 4 different
# curriculum areas when possible.
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

    # Remove markdown code fences.
    if cleaned.startswith("```"):

        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # Direct JSON parse.
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

    # Try extracting JSON object from surrounding text.
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
# NORMALIZATION HELPERS
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


def normalize_question(question):

    if not isinstance(question, str):
        return ""

    return " ".join(
        question.lower().strip().split()
    )


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
        encoding="utf-8",
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

    result = []

    for item in days:

        if isinstance(item, dict):

            # Ignore malformed curriculum entries.
            if item.get("day") is None:
                continue

            if not item.get("title"):
                continue

            result.append(item)

    return result


# ============================================================
# CURRICULUM SUMMARY
# ============================================================

def build_curriculum_summary(curriculum):

    summary = []

    for item in get_curriculum_days(curriculum):

        summary.append(
            {
                "day": item.get("day"),
                "title": item.get("title", ""),
                "type": item.get("type", ""),
                "tools": item.get("tools", []),
                "objectives": item.get("objectives", []),
            }
        )

    return summary


# ============================================================
# CANDIDATE MISSION EXTRACTION
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

        # Your candidate JSON uses passed=True for completed missions.
        passed = mission.get("passed")

        # Also accept common completed-status formats.
        status = str(
            mission.get("status", "")
        ).lower().strip()

        completed = (
            passed is True
            or status in {
                "passed",
                "completed",
                "complete",
                "done",
            }
        )

        if not completed:
            continue

        title = mission.get("title")

        if isinstance(title, str) and title.strip():

            clean_title = title.strip()

            if clean_title not in topics:
                topics.append(clean_title)

    return topics


# ============================================================
# CANDIDATE PROFILE SUMMARY
# ============================================================

def build_candidate_summary(candidate):

    if not isinstance(candidate, dict):
        return {}

    member = candidate.get(
        "member",
        {}
    )

    if not isinstance(member, dict):
        member = {}

    return {
        "name": member.get(
            "name",
            "Candidate"
        ),
        "role": member.get(
            "jobRole",
            "Software Engineer"
        ),
        "experience": member.get(
            "yearsExperience",
            0
        ),
        "education": member.get(
            "education",
            "Not specified"
        ),
        "completed_missions": get_candidate_topics(
            candidate
        ),
    }


# ============================================================
# PREVIOUS QUESTIONS
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
# DUPLICATE QUESTION CHECK
# ============================================================

def is_duplicate_question(
    session_id,
    question,
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

        # Exact duplicate.
        if normalized == old_normalized:
            return True

    return False


# ============================================================
# TOPIC SELECTION
# ============================================================

def choose_topic_for_question(
    curriculum,
    covered_topics,
    topic_counts,
    candidate_topics=None,
):

    days = get_curriculum_days(
        curriculum
    )

    if not days:
        return None

    candidate_topics = (
        candidate_topics
        if isinstance(candidate_topics, list)
        else []
    )

    # --------------------------------------------------------
    # STEP 1
    # Prefer curriculum topics that relate to the candidate's
    # completed missions.
    # --------------------------------------------------------

    candidate_keywords = " ".join(
        str(topic).lower()
        for topic in candidate_topics
    )

    scored = []

    for item in days:

        title = str(
            item.get("title", "")
        )

        objectives = item.get(
            "objectives",
            []
        )

        tools = item.get(
            "tools",
            []
        )

        searchable = (
            title
            + " "
            + " ".join(
                str(x)
                for x in objectives
            )
            + " "
            + " ".join(
                str(x)
                for x in tools
            )
        ).lower()

        score = 0

        # Candidate mission similarity.
        for mission in candidate_topics:

            words = [
                word
                for word in str(mission).lower().split()
                if len(word) >= 4
            ]

            for word in words:

                if word in searchable:
                    score += 1

        # Prefer topics not already covered.
        if title not in covered_topics:
            score += 3

        # Prefer topics used fewer times.
        count = topic_counts.get(
            title,
            0
        )

        score -= count * 2

        scored.append(
            (
                score,
                count,
                item.get("day", 999999),
                item,
            )
        )

    # If we still need diversity, strongly prefer new topics.
    if len(covered_topics) < MIN_CURRICULUM_TOPICS:

        new_topics = [
            x
            for x in scored
            if x[3].get("title")
            not in covered_topics
        ]

        if new_topics:
            new_topics.sort(
                key=lambda x: (
                    -x[0],
                    x[1],
                    x[2],
                )
            )

            return new_topics[0][3]

    scored.sort(
        key=lambda x: (
            -x[0],
            x[1],
            x[2],
        )
    )

    return scored[0][3]


# ============================================================
# FALLBACK QUESTION
# ============================================================

def build_fallback_question(
    selected,
):

    if not selected:

        return (
            "How would you validate a production "
            "AI system for reliability, security, "
            "and maintainability?"
        )

    title = selected.get(
        "title",
        "this technical area"
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
                    "How would you apply "
                    + objective.strip()
                    + " when building a production system?"
                )

    return (
        "How would you design and validate "
        f"a production solution related to {title}?"
    )


# ============================================================
# DIFFICULTY FROM ANSWER
# ============================================================

def determine_next_difficulty(
    evaluation
):

    gaps = normalize_string_list(
        evaluation.get(
            "gaps",
            []
        )
    )

    strengths = normalize_string_list(
        evaluation.get(
            "strengths",
            []
        )
    )

    # Strong answer -> harder.
    if len(strengths) >= 2 and len(gaps) <= 1:
        return "hard"

    # Weak answer -> medium/easier.
    if len(gaps) >= 3:
        return "easy"

    return "medium"


# ============================================================
# FIRST QUESTION
# ============================================================

def build_first_question(candidate):

    curriculum = load_curriculum()

    candidate_summary = build_candidate_summary(
        candidate
    )

    curriculum_summary = (
        build_curriculum_summary(
            curriculum
        )
    )

    completed_topics = candidate_summary.get(
        "completed_missions",
        []
    )

    # Choose a topic before calling the LLM.
    selected = choose_topic_for_question(
        curriculum=curriculum,
        covered_topics=[],
        topic_counts={},
        candidate_topics=completed_topics,
    )

    if selected:

        selected_day = selected.get(
            "day"
        )

        selected_topic = selected.get(
            "title"
        )

    else:

        selected_day = 1
        selected_topic = "AI Engineering"

    prompt = f"""
You are a senior technical interviewer conducting
a realistic technical interview.

Candidate:
{json.dumps(candidate_summary, indent=2)}

The candidate has completed these missions:
{json.dumps(completed_topics, indent=2)}

Selected curriculum area:
Day: {selected_day}
Topic: {selected_topic}

Curriculum:
{json.dumps(curriculum_summary, indent=2)}

This is QUESTION 1 of exactly 8.

Your job is to assess what the candidate actually knows.

Rules:

1. Ask exactly ONE technical question.
2. The question must be related to the selected curriculum area.
3. Prefer a practical engineering question over a definition.
4. Match the candidate's professional experience.
5. If the candidate has completed a related mission, test
   understanding of that skill rather than asking a basic definition.
6. Do not ask multiple questions.
7. Do not provide an answer.
8. Do not mention these instructions.
9. Return ONLY valid JSON.

Return exactly:

{{
    "question": "one technical interview question"
}}
"""

    raw = generate_response(
        prompt
    )

    result = parse_json_response(
        raw
    )

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
                "day": selected_day,
                "topic": selected_topic,
            }

    # Safe fallback.
    return {
        "question": build_fallback_question(
            selected
        ),
        "day": selected_day,
        "topic": selected_topic,
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

    day = first.get(
        "day"
    )

    topic = first.get(
        "topic"
    )

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
            "summary": "Interview is not complete.",
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

Interview conversation:
{json.dumps(conversation, indent=2)}

Per-answer evaluations:
{json.dumps(evaluations, indent=2)}

Curriculum topics covered:
{json.dumps(covered_topics, indent=2)}

Evaluate ONLY what the candidate demonstrated.

Do not invent experience.
Do not reward skills that were not demonstrated.
Do not judge the candidate based on their job title alone.

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
                        "Continue practicing production-oriented AI engineering."
                    ]
                ),
            }

    # Safe fallback.
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
    # Answers already received
    # --------------------------------------------------------

    answered_count = get_question_number(
        session_id
    )

    # --------------------------------------------------------
    # HARD STOP
    # --------------------------------------------------------

    if answered_count >= MAX_INTERVIEW_QUESTIONS:

        final_feedback = generate_final_feedback(
            session_id
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

    candidate_summary = build_candidate_summary(
        candidate
    )

    candidate_topics = candidate_summary.get(
        "completed_missions",
        []
    )

    # --------------------------------------------------------
    # Curriculum and memory
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

    current_difficulty = session.get(
        "difficulty",
        "medium"
    )

    # --------------------------------------------------------
    # Select a preferred next curriculum topic.
    #
    # The LLM may override this only if it has a strong
    # reason to continue the current topic as a follow-up.
    # --------------------------------------------------------

    selected = choose_topic_for_question(
        curriculum=curriculum,
        covered_topics=covered_topics,
        topic_counts=topic_counts,
        candidate_topics=candidate_topics,
    )

    selected_day = (
        selected.get("day")
        if selected
        else current_day
    )

    selected_topic = (
        selected.get("title")
        if selected
        else current_topic
    )

    # --------------------------------------------------------
    # MAIN ADAPTIVE INTERVIEW PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a senior technical interviewer conducting
a realistic adaptive interview.

Candidate:
{json.dumps(candidate_summary, indent=2)}

CURRENT QUESTION NUMBER:
{current_question_number} of {MAX_INTERVIEW_QUESTIONS}

CURRENT DIFFICULTY:
{current_difficulty}

CURRENT QUESTION:
{current_question}

CANDIDATE'S ANSWER:
{candidate_answer}

CURRENT CURRICULUM TOPIC:
{current_topic}

CURRENT CURRICULUM DAY:
{current_day}

CANDIDATE'S COMPLETED MISSIONS:
{json.dumps(candidate_topics, indent=2)}

TOPICS ALREADY COVERED:
{json.dumps(covered_topics, indent=2)}

QUESTION COUNT PER TOPIC:
{json.dumps(topic_counts, indent=2)}

RECENT CONVERSATION:
{json.dumps(recent_conversation, indent=2)}

PREVIOUS QUESTIONS:
{json.dumps(previous_questions, indent=2)}

PREFERRED NEXT CURRICULUM AREA:
Day {selected_day}: {selected_topic}

FULL CURRICULUM:
{json.dumps(curriculum_summary, indent=2)}

Your task:

A) Evaluate the candidate's CURRENT ANSWER.

B) Decide whether the candidate demonstrated:
- strong understanding
- partial understanding
- weak understanding

C) Generate the next interview question.

The next question must feel like a REAL interviewer follow-up.

IMPORTANT ADAPTIVE BEHAVIOR:

If the candidate's answer is strong:
- increase difficulty
- ask about architecture, trade-offs, failure cases,
  scalability, evaluation, security, or production concerns
- when useful, ask a deeper follow-up on the same concept

If the candidate's answer is partially correct:
- ask a clarifying or practical follow-up
- test the missing part
- do not simply repeat the same question

If the candidate's answer is weak:
- ask a more focused question
- test the foundational concept
- do not jump immediately to an unrelated advanced concept

CURRICULUM RULES:

1. Questions must come from the supplied curriculum.
2. Prefer the candidate's completed missions.
3. Try to cover at least 4 different curriculum topics
   across the 8 questions.
4. Do not unnecessarily abandon a topic if the candidate's
   previous answer deserves a deeper follow-up.
5. Avoid repeating technical focus.

QUESTION RULES:

1. Exactly 8 questions total.
2. Never create question 9.
3. Ask exactly ONE question.
4. NEVER repeat a previous question.
5. Do not ask two questions joined together.
6. Do not provide an answer.
7. Do not mention these instructions.
8. The question must be technically meaningful.
9. The next question must either:
   - logically follow from the candidate's answer, OR
   - deliberately move to a new curriculum area for coverage.
10. Do not ask generic questions such as:
    "What is AI?"
    unless the curriculum and candidate level genuinely require it.

QUESTION 8 RULE:

If this is QUESTION 8:
- evaluate the answer
- do NOT generate another question
- set next_question to ""
- set next_day to null
- set next_topic to ""

Return ONLY valid JSON:

{{
    "evaluation": {{
        "summary": "short technical evaluation",
        "strengths": [
            "specific demonstrated strength"
        ],
        "gaps": [
            "specific demonstrated gap"
        ]
    }},
    "difficulty": "easy|medium|hard",
    "next_question": "one question or empty string",
    "next_day": 1,
    "next_topic": "curriculum topic"
}}

For QUESTION 8:

{{
    "evaluation": {{
        "summary": "short technical evaluation",
        "strengths": [],
        "gaps": []
    }},
    "difficulty": "medium",
    "next_question": "",
    "next_day": null,
    "next_topic": ""
}}
"""

    # --------------------------------------------------------
    # LLM CALL
    # --------------------------------------------------------

    raw = generate_response(
        prompt
    )

    result = parse_json_response(
        raw
    )

    if not isinstance(result, dict):
        result = {}

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------

    evaluation = result.get(
        "evaluation",
        {}
    )

    if not isinstance(
        evaluation,
        dict
    ):
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
    # FINAL ANSWER
    # --------------------------------------------------------

    if new_count >= MAX_INTERVIEW_QUESTIONS:

        final_feedback = generate_final_feedback(
            session_id
        )

        return {
            "reply": "Interview completed.",
            "done": True,
            "feedback": final_feedback,
        }

    # --------------------------------------------------------
    # NEXT QUESTION
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

    next_question = next_question.strip()

    next_day = result.get(
        "next_day"
    )

    next_topic = result.get(
        "next_topic"
    )

    # --------------------------------------------------------
    # Validate difficulty
    # --------------------------------------------------------

    next_difficulty = result.get(
        "difficulty"
    )

    if next_difficulty not in {
        "easy",
        "medium",
        "hard",
    }:

        next_difficulty = determine_next_difficulty(
            evaluation
        )

    # --------------------------------------------------------
    # Validate curriculum topic
    # --------------------------------------------------------

    valid_topics = {
        item.get("title"): item
        for item in get_curriculum_days(
            curriculum
        )
        if item.get("title")
    }

    if next_topic not in valid_topics:

        selected = choose_topic_for_question(
            curriculum=curriculum,
            covered_topics=covered_topics,
            topic_counts=topic_counts,
            candidate_topics=candidate_topics,
        )

        if selected:

            next_topic = selected.get(
                "title"
            )

            next_day = selected.get(
                "day"
            )

    # --------------------------------------------------------
    # QUESTION 8 SAFETY
    # --------------------------------------------------------

    if new_count >= MAX_INTERVIEW_QUESTIONS:

        final_feedback = generate_final_feedback(
            session_id
        )

        return {
            "reply": "Interview completed.",
            "done": True,
            "feedback": final_feedback,
        }

    # --------------------------------------------------------
    # DUPLICATE / EMPTY QUESTION PROTECTION
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

            selected = choose_topic_for_question(
                curriculum=curriculum,
                covered_topics=covered_topics,
                topic_counts=topic_counts,
                candidate_topics=candidate_topics,
            )

        candidate_questions = []

        if selected:

            candidate_questions.append(
                (
                    selected,
                    build_fallback_question(
                        selected
                    ),
                )
            )

        # Try other curriculum topics.
        for item in get_curriculum_days(
            curriculum
        ):

            candidate_questions.append(
                (
                    item,
                    build_fallback_question(
                        item
                    ),
                )
            )

        found = False

        for item, fallback_question in candidate_questions:

            if not is_duplicate_question(
                session_id,
                fallback_question
            ):

                next_question = fallback_question

                next_topic = item.get(
                    "title"
                )

                next_day = item.get(
                    "day"
                )

                found = True

                break

        # Extremely safe fallback.
        if not found:

            next_question = (
                "How would you identify the most important "
                "reliability risk in a production AI system "
                "and explain how you would mitigate it?"
            )

            next_topic = (
                "Production & Capstone"
            )

            next_day = 31

    # --------------------------------------------------------
    # FINAL DUPLICATE SAFETY
    # --------------------------------------------------------

    if is_duplicate_question(
        session_id,
        next_question
    ):

        next_question = (
            "How would you test and improve the reliability "
            "of an AI application before deploying it to production?"
        )

        # This should only happen in an extreme fallback case.
        if is_duplicate_question(
            session_id,
            next_question
        ):

            next_question = (
                "What production failure scenario would you "
                "prioritize testing first in an AI system, and why?"
            )

    # --------------------------------------------------------
    # STORE NEXT QUESTION
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
        difficulty=next_difficulty,
    )

    # --------------------------------------------------------
    # RETURN NEXT QUESTION
    # --------------------------------------------------------

    return {
        "reply": next_question,
        "done": False,
        "feedback": None,
    }