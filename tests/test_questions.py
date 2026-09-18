from opticprep.models import DIFFICULTIES, TOPICS
from opticprep.questions import CURATED_QUESTIONS


def test_curated_bank_has_expected_shape_and_count():
    assert len(CURATED_QUESTIONS) >= 30
    assert len({question.id for question in CURATED_QUESTIONS}) == len(CURATED_QUESTIONS)
    assert {question.topic for question in CURATED_QUESTIONS} == set(TOPICS)
    assert {question.difficulty for question in CURATED_QUESTIONS} == set(DIFFICULTIES)
    assert all(len(question.options) == 4 for question in CURATED_QUESTIONS)
    assert all(len(set(question.options)) == 4 for question in CURATED_QUESTIONS)
    assert all(question.source == "curated" for question in CURATED_QUESTIONS)

