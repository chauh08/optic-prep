import json
from functools import lru_cache
from pathlib import Path

from opticprep.models import Question


@lru_cache(maxsize=1)
def load_questions() -> tuple[Question, ...]:
    path = Path(__file__).resolve().parent / "questions.json"
    return tuple(Question.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8")))


CURATED_QUESTIONS = load_questions()
