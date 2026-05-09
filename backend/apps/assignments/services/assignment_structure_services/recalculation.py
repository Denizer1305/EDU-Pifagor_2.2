from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.assignments.models import (
    Assignment,
    AssignmentPolicy,
    AssignmentVariant,
)
from apps.assignments.services.assignment_structure_services.common import sum_decimal


@transaction.atomic
def recalculate_assignment_variant_max_score(
    variant: AssignmentVariant | None,
) -> AssignmentVariant | None:
    """Пересчитывает максимальный балл варианта по сумме вопросов."""

    if variant is None:
        return None

    variant.max_score = sum_decimal(
        variant.questions.all(),
        "max_score",
    )
    variant.full_clean()
    variant.save(update_fields=("max_score", "updated_at"))
    return variant


@transaction.atomic
def recalculate_assignment_policy_max_score(assignment: Assignment) -> AssignmentPolicy:
    """Пересчитывает максимальный балл политики работы."""

    policy, _ = AssignmentPolicy.objects.get_or_create(
        assignment=assignment,
        defaults={
            "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
            "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            "max_score": 0,
            "passing_score": 0,
            "attempts_limit": 1,
            "allow_text_answer": True,
        },
    )

    if assignment.variants.exists():
        default_variant = (
            assignment.variants.filter(is_default=True).order_by("order", "id").first()
            or assignment.variants.order_by("order", "id").first()
        )
        max_score = default_variant.max_score if default_variant else Decimal("0")
    else:
        max_score = sum_decimal(assignment.questions.all(), "max_score")

    policy.max_score = max_score
    if policy.passing_score > policy.max_score:
        policy.passing_score = policy.max_score

    policy.full_clean()
    policy.save(update_fields=("max_score", "passing_score", "updated_at"))
    return policy
