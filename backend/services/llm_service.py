"""LLM service — OpenRouter API via ChatLiteLLM (LangSmith-traced)."""

import json
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage
from config import OPENROUTER_API_KEY, LLM_MODEL


def _get_llm(temperature: float = 0.7) -> ChatLiteLLM:
    """Create a ChatLiteLLM instance (auto-traced by LangSmith)."""
    return ChatLiteLLM(
        model=LLM_MODEL,
        api_key=OPENROUTER_API_KEY,
        temperature=temperature,
        max_tokens=4096,
    )


def generate_text(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """Generate text from the LLM."""
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    llm = _get_llm(temperature=temperature)
    response = llm.invoke(messages)
    return response.content


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
        first_brace = raw.find("{")
        first_bracket = raw.find("[")
        
        if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
            start = first_bracket
            end = raw.rfind("]") + 1
        elif first_brace != -1:
            start = first_brace
            end = raw.rfind("}") + 1
        else:
            start = -1
            end = -1
            
        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError as e:
                raise ValueError(f"LLM did not return valid JSON. Error: {str(e)}\nRaw: {raw[:200]}")
        raise ValueError(f"LLM did not return valid JSON: {raw[:200]}")

