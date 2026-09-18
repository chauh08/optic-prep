import json

import pytest
from pydantic import ValidationError

from opticprep.ai import AIUnavailable, generate_questions
from opticprep.models import GeneratedResponse


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def model_payload(questions):
    return {"choices": [{"message": {"content": json.dumps({"questions": questions})}}]}


def valid_item(**updates):
    item = {
        "prompt": "Which optical property describes resistance to scratching?",
        "options": ["Abbe value", "Surface hardness", "Specific gravity", "Index"],
        "correctIndex": 1,
        "rationale": "Surface hardness most directly describes scratch resistance.",
        "topic": "Ophthalmic lenses",
        "difficulty": "foundation",
    }
    item.update(updates)
    return item


def test_generated_schema_rejects_duplicate_options_and_extra_fields():
    with pytest.raises(ValidationError):
        GeneratedResponse.model_validate(
            {"questions": [valid_item(options=["same", "same", "third", "fourth"])]}
        )
    with pytest.raises(ValidationError):
        GeneratedResponse.model_validate({"questions": [valid_item(secret="not allowed")]})


def test_generation_validates_filters_and_never_sends_token_in_output():
    captured = {}

    def fake_post(url, **kwargs):
        captured.update(kwargs)
        return FakeResponse(model_payload([valid_item()]))

    questions = generate_questions(
        1,
        ["Ophthalmic lenses"],
        ["foundation"],
        [],
        token="test-secret",
        post=fake_post,
    )
    assert len(questions) == 1
    assert questions[0].source == "ai"
    assert captured["headers"]["Authorization"] == "Bearer test-secret"
    assert "test-secret" not in questions[0].model_dump_json()


def test_generation_rejects_wrong_topic_and_duplicate_prompt():
    item = valid_item()

    def fake_post(*args, **kwargs):
        return FakeResponse(model_payload([item]))

    with pytest.raises(AIUnavailable, match="requested filters"):
        generate_questions(
            1,
            ["Dispensing"],
            ["foundation"],
            [],
            token="token",
            post=fake_post,
        )
    with pytest.raises(AIUnavailable, match="requested filters"):
        generate_questions(
            1,
            ["Ophthalmic lenses"],
            ["foundation"],
            [item["prompt"]],
            token="token",
            post=fake_post,
        )


def test_generation_without_token_has_explicit_fallback_error(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr("opticprep.ai.get_secret", lambda name: None)
    with pytest.raises(AIUnavailable, match="not configured"):
        generate_questions(1, ["Dispensing"], ["foundation"], [])


def test_generation_rejects_non_string_model_content():
    def fake_post(*args, **kwargs):
        return FakeResponse({"choices": [{"message": {"content": None}}]})

    with pytest.raises(AIUnavailable, match="safely validated"):
        generate_questions(
            1,
            ["Dispensing"],
            ["foundation"],
            [],
            token="token",
            post=fake_post,
        )
