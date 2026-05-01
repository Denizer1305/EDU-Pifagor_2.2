from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.assignments.models import Assignment, AssignmentVariant
from apps.assignments.services.assignment_structure_services.recalculation import (
    recalculate_assignment_policy_max_score,
    recalculate_assignment_variant_max_score,
)


@transaction.atomic
def create_assignment_variant(
    *,
    assignment: Assignment,
    title: str,
    code: str = "",
    description: str = "",
    variant_number: int,
    order: int = 1,
    is_default: bool = False,
    max_score=0,
    is_active: bool = True,
) -> AssignmentVariant:
    """Создаёт вариант работы."""

    variant = AssignmentVariant(
        assignment=assignment,
        title=title,
        code=code,
        description=description,
        variant_number=variant_number,
        order=order,
        is_default=is_default,
        max_score=max_score,
        is_active=is_active,
    )
    variant.full_clean()
    variant.save()

    recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(assignment)
    return variant


@transaction.atomic
def update_assignment_variant(variant: AssignmentVariant, **fields) -> AssignmentVariant:
    """Обновляет вариант работы."""

    for field_name, value in fields.items():
        setattr(variant, field_name, value)

    variant.full_clean()
    variant.save()

    recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(variant.assignment)
    return variant


@transaction.atomic
def delete_assignment_variant(variant: AssignmentVariant) -> None:
    """Удаляет вариант работы и пересчитывает максимальный балл."""

    assignment = variant.assignment
    variant.delete()
    recalculate_assignment_policy_max_score(assignment)


@transaction.atomic
def reorder_assignment_variants(
    *,
    assignment: Assignment,
    variant_ids_in_order: list[int],
) -> list[AssignmentVariant]:
    """Меняет порядок вариантов работы."""

    variants = list(
        AssignmentVariant.objects.filter(
            assignment=assignment,
            id__in=variant_ids_in_order,
        )
    )
    variants_map = {variant.id: variant for variant in variants}

    if len(variants_map) != len(variant_ids_in_order):
        raise ValidationError("Не все варианты найдены.")

    temp_base = 1000

    for index, variant_id in enumerate(variant_ids_in_order, start=1):
        variant = variants_map[variant_id]
        variant.order = temp_base + index
        variant.variant_number = temp_base + index
        variant.is_default = index == 1

    AssignmentVariant.objects.bulk_update(
        variants,
        ["order", "variant_number", "is_default", "updated_at"],
    )

    for index, variant_id in enumerate(variant_ids_in_order, start=1):
        variant = variants_map[variant_id]
        variant.order = index
        variant.variant_number = index

    AssignmentVariant.objects.bulk_update(
        variants,
        ["order", "variant_number", "updated_at"],
    )

    return list(
        AssignmentVariant.objects.filter(assignment=assignment).order_by("order", "id")
    )
