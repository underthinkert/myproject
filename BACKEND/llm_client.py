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
        "OPENAI_API_KEY is missing. "
        "Make sure your .env file contains OPENAI_API_KEY."
    )


# ============================================================
# CLIENT
# ============================================================

client = OpenAI(
    api_key=api_key,
    base_url=os.getenv(
        "OPENAI_BASE_URL",
        "https://openrouter.ai/api/v1"
    )
)


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(prompt: str):

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    response = client.responses.create(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        ),
        input=prompt,
        max_output_tokens=1000
    )

    return response.output_text.strip()