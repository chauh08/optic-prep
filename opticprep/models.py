from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TOPICS = (
    "Optics fundamentals",
    "Ophthalmic lenses",
    "Frame fitting & measurements",
    "Dispensing",
    "Ocular anatomy & refractive conditions",
    "Instrumentation & verification",
    "Safety & regulatory basics",
)
DIFFICULTIES = ("foundation", "applied", "challenge")

Topic = Literal[
    "Optics fundamentals",
    "Ophthalmic lenses",
    "Frame fitting & measurements",
    "Dispensing",
    "Ocular anatomy & refractive conditions",
    "Instrumentation & verification",
    "Safety & regulatory basics",
]
Difficulty = Literal["foundation", "applied", "challenge"]


def normalize_prompt(value: str) -> str:
    return " ".join("".join(char.lower() if char.isalnum() else " " for char in value).split())


def normalize_option(value: str) -> str:
    return " ".join(value.casefold().split())


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=12, max_length=500)
    options: tuple[str, str, str, str]
    correctIndex: int = Field(ge=0, le=3)
    rationale: str = Field(min_length=12, max_length=600)
    topic: Topic
    difficulty: Difficulty
    source: Literal["curated", "ai"]

    @field_validator("prompt", "rationale", "id")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("options")
    @classmethod
    def validate_options(cls, options: tuple[str, str, str, str]) -> tuple[str, str, str, str]:
        cleaned = tuple(option.strip() for option in options)
        if any(not option or len(option) > 180 for option in cleaned):
            raise ValueError("Options must be 1–180 characters.")
        if len({normalize_option(option) for option in cleaned}) != 4:
            raise ValueError("All four options must be distinct.")
        return cleaned


class GeneratedQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=12, max_length=500)
    options: tuple[str, str, str, str]
    correctIndex: int = Field(ge=0, le=3)
    rationale: str = Field(min_length=12, max_length=600)
    topic: Topic
    difficulty: Difficulty

    @field_validator("prompt", "rationale")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("options")
    @classmethod
    def validate_options(cls, options: tuple[str, str, str, str]) -> tuple[str, str, str, str]:
        cleaned = tuple(option.strip() for option in options)
        if any(not option or len(option) > 180 for option in cleaned):
            raise ValueError("Options must be 1–180 characters.")
        if len({normalize_option(option) for option in cleaned}) != 4:
            raise ValueError("All four options must be distinct.")
        return cleaned


class GeneratedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[GeneratedQuestion] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def reject_duplicate_prompts(self) -> "GeneratedResponse":
        prompts = [normalize_prompt(question.prompt) for question in self.questions]
        if len(prompts) != len(set(prompts)):
            raise ValueError("Generated prompts must be unique.")
        return self
