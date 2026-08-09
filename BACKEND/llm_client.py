import os

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GET CONFIGURATION
# ============================================================

api_key = os.getenv("OPENAI_API_KEY")

base_url = os.getenv(
    "OPENAI_BASE_URL",
    "https://openrouter.ai/api/v1"
)

model = os.getenv(
    "OPENAI_MODEL",
    "openai/gpt-4o-mini"
)


# ============================================================
# VALIDATE API KEY
# ============================================================

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing."
    )


# ============================================================
# CLIENT
# ============================================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(prompt: str):

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    print("========================================")
    print("AI API CALL STARTED")
    print("Provider: OpenRouter")
    print("Base URL:", base_url)
    print("Model:", model)
    print("========================================")

    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=1000
    )

    result = response.output_text.strip()

    print("========================================")
    print("AI API CALL SUCCESSFUL")
    print("Model:", model)
    print("========================================")

    return result