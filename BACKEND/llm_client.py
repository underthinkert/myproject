import os

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

api_key = os.getenv("OPENROUTER_API_KEY")

base_url = os.getenv(
    "OPENAI_BASE_URL",
    "https://openrouter.ai/api/v1"
)

model = os.getenv(
    "OPENAI_MODEL",
    "openai/gpt-4o-mini"
)


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

if not api_key:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing. "
        "Add it to your local .env file or Render environment variables."
    )


# ============================================================
# OPENAI-COMPATIBLE CLIENT
# ============================================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(prompt: str) -> str:

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

    try:

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=1200,
            temperature=0.4,
        )

        if not response.choices:
            raise RuntimeError(
                "OpenRouter returned no choices."
            )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "OpenRouter returned an empty response."
            )

        result = content.strip()

        print("========================================")
        print("AI API CALL SUCCESSFUL")
        print("Provider: OpenRouter")
        print("Model:", model)
        print("========================================")

        return result

    except Exception as e:

        print("========================================")
        print("AI API CALL FAILED")
        print("Provider: OpenRouter")
        print("Error:", str(e))
        print("========================================")

        raise RuntimeError(
            f"OpenRouter API request failed: {str(e)}"
        ) from e