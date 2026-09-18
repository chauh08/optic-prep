from __future__ import annotations

from decimal import Decimal

from opticprep.models import Question


def _signed(value: Decimal) -> str:
    return f"{value:+.2f}".replace("-", "−")


def _rotate(options: list[str], correct: str, offset: int) -> tuple[tuple[str, str, str, str], int]:
    rotated = options[offset:] + options[:offset]
    return tuple(rotated), rotated.index(correct)


def _focal_variants() -> list[Question]:
    cases = (
        ("nv-fl-01", Decimal("0.80"), 0),
        ("nv-fl-02", Decimal("-0.40"), 2),
        ("nv-fl-03", Decimal("0.25"), 3),
    )
    questions = []
    for question_id, focal_length, offset in cases:
        power = Decimal("1") / focal_length
        correct = f"{_signed(power)} D"
        options, correct_index = _rotate(
            [
                correct,
                f"{_signed(-power)} D",
                f"{_signed(focal_length)} D",
                f"{_signed(-focal_length)} D",
            ],
            correct,
            offset,
        )
        questions.append(
            Question(
                id=question_id,
                prompt=(
                    f"A thin lens has a focal length of {_signed(focal_length)} meter in air. "
                    "What is its approximate power?"
                ),
                options=options,
                correctIndex=correct_index,
                rationale=(
                    "Power equals the reciprocal of focal length in meters: "
                    f"1 ÷ {_signed(focal_length)} = {_signed(power)} D."
                ),
                topic="Optics fundamentals",
                difficulty="applied",
                source="curated",
            )
        )
    return questions


def _prentice_variants() -> list[Question]:
    cases = (
        ("nv-pr-01", Decimal("2.50"), Decimal("8"), 1),
        ("nv-pr-02", Decimal("6.00"), Decimal("3"), 2),
        ("nv-pr-03", Decimal("-3.50"), Decimal("4"), 3),
    )
    questions = []
    for question_id, power, millimeters, offset in cases:
        prism = abs(power) * millimeters / Decimal("10")
        correct = f"{prism:.2f} prism diopters"
        options, correct_index = _rotate(
            [
                correct,
                f"{abs(power):.2f} prism diopters",
                f"{millimeters / Decimal('10'):.2f} prism diopters",
                f"{abs(power) * millimeters:.2f} prism diopters",
            ],
            correct,
            offset,
        )
        questions.append(
            Question(
                id=question_id,
                prompt=(
                    f"What is the magnitude of prism induced {millimeters:.0f} mm from the "
                    f"optical center of a {_signed(power)} D lens?"
                ),
                options=options,
                correctIndex=correct_index,
                rationale=(
                    "Prentice’s rule uses decentration in centimeters: "
                    f"{millimeters / Decimal('10'):.2f} cm × {abs(power):.2f} D "
                    f"= {prism:.2f} prism diopters."
                ),
                topic="Optics fundamentals",
                difficulty="applied",
                source="curated",
            )
        )
    return questions


def _frame_pd_variants() -> list[Question]:
    cases = (
        ("nv-pd-01", 48, 17, 1),
        ("nv-pd-02", 54, 16, 2),
        ("nv-pd-03", 51, 19, 3),
    )
    questions = []
    for question_id, eye_size, bridge, offset in cases:
        frame_pd = eye_size + bridge
        correct = f"{frame_pd} mm"
        options, correct_index = _rotate(
            [
                correct,
                f"{eye_size} mm",
                f"{bridge} mm",
                f"{eye_size - bridge} mm",
            ],
            correct,
            offset,
        )
        questions.append(
            Question(
                id=question_id,
                prompt=(
                    f"A frame is marked {eye_size}□{bridge}. What is its frame PD in the "
                    "boxing system?"
                ),
                options=options,
                correctIndex=correct_index,
                rationale=(
                    "Frame PD equals boxed eye size plus distance between lenses: "
                    f"{eye_size} + {bridge} = {frame_pd} mm."
                ),
                topic="Frame fitting & measurements",
                difficulty="applied",
                source="curated",
            )
        )
    return questions


def _transposition_variants() -> list[Question]:
    cases = (
        ("nv-tr-01", Decimal("2.00"), Decimal("1.50"), 45, 1),
        ("nv-tr-02", Decimal("-1.00"), Decimal("-2.00"), 180, 2),
        ("nv-tr-03", Decimal("0.50"), Decimal("-1.25"), 70, 3),
    )
    questions = []
    for question_id, sphere, cylinder, axis, offset in cases:
        new_sphere = sphere + cylinder
        new_cylinder = -cylinder
        new_axis = axis + 90 if axis <= 90 else axis - 90
        source = f"{_signed(sphere)} {_signed(cylinder)} × {axis:03d}"
        correct = f"{_signed(new_sphere)} {_signed(new_cylinder)} × {new_axis:03d}"
        options, correct_index = _rotate(
            [
                correct,
                f"{_signed(new_sphere)} {_signed(cylinder)} × {new_axis:03d}",
                f"{_signed(sphere)} {_signed(new_cylinder)} × {axis:03d}",
                f"{_signed(new_sphere)} {_signed(new_cylinder)} × {axis:03d}",
            ],
            correct,
            offset,
        )
        questions.append(
            Question(
                id=question_id,
                prompt=f"Which prescription is the correct transposition of {source}?",
                options=options,
                correctIndex=correct_index,
                rationale=(
                    "Add sphere and cylinder for the new sphere, reverse the cylinder sign, "
                    f"and rotate the axis 90°: {correct}."
                ),
                topic="Ophthalmic lenses",
                difficulty="challenge",
                source="curated",
            )
        )
    return questions


def build_numeric_variants() -> tuple[Question, ...]:
    """Build a deterministic set of original calculation variants."""
    return tuple(
        _focal_variants()
        + _prentice_variants()
        + _frame_pd_variants()
        + _transposition_variants()
    )


NUMERIC_VARIANTS = build_numeric_variants()
