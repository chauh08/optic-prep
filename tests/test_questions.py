from collections import Counter

from opticprep.models import DIFFICULTIES, TOPICS, normalize_prompt
from opticprep.questions import CURATED_QUESTIONS
from opticprep.variants import NUMERIC_VARIANTS, build_numeric_variants


def test_curated_bank_has_expected_shape_and_count():
    assert len(CURATED_QUESTIONS) >= 75
    assert len({question.id for question in CURATED_QUESTIONS}) == len(CURATED_QUESTIONS)
    assert len({normalize_prompt(question.prompt) for question in CURATED_QUESTIONS}) == len(
        CURATED_QUESTIONS
    )
    assert {question.topic for question in CURATED_QUESTIONS} == set(TOPICS)
    assert {question.difficulty for question in CURATED_QUESTIONS} == set(DIFFICULTIES)
    assert all(len(question.options) == 4 for question in CURATED_QUESTIONS)
    assert all(len(set(question.options)) == 4 for question in CURATED_QUESTIONS)
    assert all(question.source == "curated" for question in CURATED_QUESTIONS)


def test_every_topic_has_every_difficulty_with_representative_depth():
    coverage = Counter((question.topic, question.difficulty) for question in CURATED_QUESTIONS)
    assert set(coverage) == {
        (topic, difficulty) for topic in TOPICS for difficulty in DIFFICULTIES
    }
    assert min(coverage.values()) >= 4


def test_numeric_variants_are_deterministic_and_have_verified_answers():
    assert build_numeric_variants() == NUMERIC_VARIANTS
    assert len(NUMERIC_VARIANTS) == 12
    expected_answers = {
        "nv-fl-01": "+1.25 D",
        "nv-fl-02": "−2.50 D",
        "nv-fl-03": "+4.00 D",
        "nv-pr-01": "2.00 prism diopters",
        "nv-pr-02": "1.80 prism diopters",
        "nv-pr-03": "1.40 prism diopters",
        "nv-pd-01": "65 mm",
        "nv-pd-02": "70 mm",
        "nv-pd-03": "70 mm",
        "nv-tr-01": "+3.50 −1.50 × 135",
        "nv-tr-02": "−3.00 +2.00 × 090",
        "nv-tr-03": "−0.75 +1.25 × 160",
    }
    assert {question.id for question in NUMERIC_VARIANTS} == set(expected_answers)
    for question in NUMERIC_VARIANTS:
        assert question.options[question.correctIndex] == expected_answers[question.id]
    assert {question.correctIndex for question in NUMERIC_VARIANTS} == {0, 1, 2, 3}
