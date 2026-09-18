import random

from opticprep.questions import CURATED_QUESTIONS
from opticprep.quiz import merge_unique, score_questions, select_questions


def test_selection_respects_count_and_filters():
    selected = select_questions(
        CURATED_QUESTIONS,
        5,
        ["Dispensing"],
        ["foundation"],
        rng=random.Random(4),
    )
    assert 0 < len(selected) <= 5
    assert all(question.topic == "Dispensing" for question in selected)
    assert all(question.difficulty == "foundation" for question in selected)


def test_scoring_and_topic_breakdown():
    questions = list(CURATED_QUESTIONS[:3])
    answers = {
        questions[0].id: questions[0].correctIndex,
        questions[1].id: (questions[1].correctIndex + 1) % 4,
    }
    result = score_questions(questions, answers)
    assert result["correct"] == 1
    assert result["total"] == 3
    assert result["by_topic"] == [{"topic": "Optics fundamentals", "correct": 1, "total": 3}]
    assert result["missed"] == questions[1:]


def test_merge_prefers_ai_and_rejects_duplicate_prompts():
    original = CURATED_QUESTIONS[0]
    duplicate = original.model_copy(update={"id": "ai-copy", "source": "ai"})
    result = merge_unique([original, CURATED_QUESTIONS[1]], [duplicate], 3)
    assert [item.id for item in result] == ["ai-copy", CURATED_QUESTIONS[1].id]

