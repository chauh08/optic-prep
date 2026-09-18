import json
import os
import time
from collections.abc import Callable, Sequence
from typing import Any

import httpx
from pydantic import ValidationError

from opticprep.models import GeneratedResponse, Question, normalize_prompt

MODELS_URL = "https://models.github.ai/inference/chat/completions"


class AIUnavailable(RuntimeError):
    """Raised when safe AI question generation is unavailable."""


def get_secret(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(name)
    except (FileNotFoundError, KeyError):
        return None


def generate_questions(
    count: int,
    topics: Sequence[str],
    difficulties: Sequence[str],
    existing_prompts: Sequence[str],
    *,
    token: str | None = None,
    model: str | None = None,
    post: Callable[..., Any] = httpx.post,
) -> list[Question]:
    token = token or get_secret("GITHUB_TOKEN")
    if not token:
        raise AIUnavailable("AI enhancement is not configured.")
    count = max(1, min(int(count), 10))
    model = model or get_secret("GITHUB_MODELS_MODEL") or "openai/gpt-4.1-mini"
    instruction = (
        f"Create {count} original opticianry practice questions. This is independent study "
        "material, not real or recalled certification exam content. "
        f"Use only these topics: {', '.join(topics)}. "
        f"Use only these difficulty labels: {', '.join(difficulties)}. "
        "Each item needs exactly four distinct plausible options, one correctIndex from 0 to 3, "
        "and a concise factual rationale. Avoid jurisdiction-specific legal claims. "
        f"Do not repeat or closely paraphrase: {' | '.join(existing_prompts)}. "
        'Return JSON only as {"questions":[{"prompt":"","options":["","","",""],'
        '"correctIndex":0,"rationale":"","topic":"","difficulty":""}]}.'
    )
    try:
        response = post(
            MODELS_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Write original, cautious educational items. Return strict JSON.",
                    },
                    {"role": "user", "content": instruction},
                ],
                "temperature": 0.5,
                "max_tokens": 3500,
                "response_format": {"type": "json_object"},
            },
            timeout=20.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("Model content must be text.")
        content = content.strip()
        if content.startswith("```"):
            content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        validated = GeneratedResponse.model_validate(json.loads(content))
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, ValidationError) as exc:
        raise AIUnavailable("AI output could not be safely validated.") from exc

    existing = {normalize_prompt(prompt) for prompt in existing_prompts}
    accepted: list[Question] = []
    for item in validated.questions:
        if item.topic not in topics or item.difficulty not in difficulties:
            continue
        if normalize_prompt(item.prompt) in existing:
            continue
        accepted.append(
            Question(
                **item.model_dump(),
                id=f"ai-{time.time_ns()}-{len(accepted)}",
                source="ai",
            )
        )
    if not accepted:
        raise AIUnavailable("AI output did not match the requested filters.")
    return accepted[:count]
