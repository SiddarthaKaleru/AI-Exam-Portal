"""LLM service — OpenRouter API via litellm."""

import json
from litellm import completion
from config import OPENROUTER_API_KEY, LLM_MODEL


def generate_text(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """Generate text from the LLM."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = completion(
        model=LLM_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=4096,
        api_key=OPENROUTER_API_KEY,
    )
    return response.choices[0].message.content


def generate_json(prompt: str, system_prompt: str = "", temperature: float = 0.3) -> dict | list:
    """Generate structured JSON from the LLM."""
    json_system = (system_prompt or "") + (
        "\n\nIMPORTANT: You MUST respond with valid JSON only. "
        "No markdown, no code blocks, no extra text — just the raw JSON."
    )

    raw = generate_text(prompt, system_prompt=json_system, temperature=temperature)

    # Clean common LLM artifacts
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1:
            start = raw.find("[")
            end = raw.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        raise ValueError(f"LLM did not return valid JSON: {raw[:200]}")
