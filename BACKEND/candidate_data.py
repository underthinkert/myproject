import json
from pathlib import Path


PROFILE_FILE = (
    Path(__file__).parent
    / "Data"
    / "candidate.json"
)


def load_candidates():
    with open(PROFILE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["candidates"]


def get_candidate(candidate_name: str):
    candidates = load_candidates()

    for candidate in candidates:
        member = candidate["member"]

        if member["name"].lower() == candidate_name.lower():
            return candidate

    return None