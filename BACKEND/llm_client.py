import os

from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

# ============================================================
# GET API KEY
# ============================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing."
    )

# ============================================================
# CLIENT
# ============================================================

client = OpenAI(
    api_key=api_key
)

# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(prompt: str):

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    print("====================================")
    print("AI API CALL STARTED")
    print(
        "Model:",
        os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        )
    )
    print("====================================")

    response = client.responses.create(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        ),
        input=prompt,
        max_output_tokens=1000
    )

    print("====================================")
    print("AI API CALL SUCCESSFUL")
    print("====================================")

    return response.output_text.strip()