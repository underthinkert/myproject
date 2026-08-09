def generate_response(prompt: str):

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    print("====================================")
    print("AI API CALL STARTED")
    print("Model:", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
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