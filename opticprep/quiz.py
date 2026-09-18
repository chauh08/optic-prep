import random
from collections import OrderedDict
from collections.abc import Iterable, Sequence

from opticprep.models import Question, normalize_prompt


def select_questions(
    bank: Sequence[Question],
    count: int,
    topics: Iterable[str],
    difficulties: Iterable[str],
    *,
    rng: random.Random | None = None,
) -> list[Question]:
    topic_set, difficulty_set = set(topics), set(difficulties)
    eligible = [q for q in bank if q.topic in topic_set and q.difficulty in difficulty_set]
    (rng or random).shuffle(eligible)
    return eligible[: min(count, len(eligible))]


def score_questions(questions: Sequence[Question], answers: dict[str, int]) -> dict:
    breakdown: OrderedDict[str, dict[str, int]] = OrderedDict()
    missed: list[Question] = []
    correct = 0
    for question in questions:
        row = breakdown.setdefault(question.topic, {"correct": 0, "total": 0})
        row["total"] += 1
        if answers.get(question.id) == question.correctIndex:
            correct += 1
            row["correct"] += 1
        else:
            missed.append(question)
    return {
        "correct": correct,
        "total": len(questions),
        "by_topic": [{"topic": topic, **values} for topic, values in breakdown.items()],
        "missed": missed,
    }


def merge_unique(
    curated: Sequence[Question], generated: Sequence[Question], limit: int
) -> list[Question]:
    candidates: list[Question] = []
    for index in range(max(len(curated), len(generated))):
        if index < len(generated):
            candidates.append(generated[index])
        if index < len(curated):
            candidates.append(curated[index])
    seen: set[str] = set()
    result: list[Question] = []
    for question in candidates:
        key = normalize_prompt(question.prompt)
        if key and key not in seen:
            seen.add(key)
            result.append(question)
        if len(result) == limit:
            break
    return result

