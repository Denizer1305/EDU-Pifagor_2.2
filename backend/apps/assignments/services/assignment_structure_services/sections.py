from __future__ import annotations

from django.db import transaction

from apps.assignments.models import Assignment, AssignmentSection
from apps.assignments.services.assignment_structure_services.recalculation import (
    recalculate_assignment_policy_max_score,
    recalculate_assignment_variant_max_score,
)


@transaction.atomic
def create_assignment_section(
    *,
    assignment: Assignment,
    title: str,
    description: str = "",
    section_type: str = AssignmentSection.SectionTypeChoices.COMMON,
    order: int = 1,
    max_score=0,
    is_required: bool = True,
    variant=None,
) -> AssignmentSection:
    """Создаёт секцию работы."""

    section = AssignmentSection(
        assignment=assignment,
        variant=variant,
        title=title,
        description=description,
        section_type=section_type,
        order=order,
        max_score=max_score,
        is_required=is_required,
    )
    section.full_clean()
    section.save()

    if variant:
        recalculate_assignment_variant_max_score(variant)

    recalculate_assignment_policy_max_score(assignment)
    return section


@transaction.atomic
def update_assignment_section(section: AssignmentSection, **fields) -> AssignmentSection:
    """Обновляет секцию работы."""

    old_variant = section.variant

    for field_name, value in fields.items():
        setattr(section, field_name, value)

    section.full_clean()
    section.save()

    if old_variant:
        recalculate_assignment_variant_max_score(old_variant)

    if section.variant:
        recalculate_assignment_variant_max_score(section.variant)

    recalculate_assignment_policy_max_score(section.assignment)
    return section


@transaction.atomic
def delete_assignment_section(section: AssignmentSection) -> None:
    """Удаляет секцию работы."""

    assignment = section.assignment
    variant = section.variant
    section.delete()

    if variant:
        recalculate_assignment_variant_max_score(variant)

    recalculate_assignment_policy_max_score(assignment)


@transaction.atomic
def reorder_assignment_sections(
    *,
    assignment: Assignment,
    section_ids_in_order: list[int],
) -> list[AssignmentSection]:
    """Меняет порядок секций работы."""

    sections = list(assignment.sections.filter(id__in=section_ids_in_order))
    sections_map = {section.id: section for section in sections}

    ordered_sections: list[AssignmentSection] = []

    for index, section_id in enumerate(section_ids_in_order, start=1):
        section = sections_map.get(section_id)
        if section is None:
            continue

        section.order = index
        section.full_clean()
        section.save(update_fields=("order", "updated_at"))
        ordered_sections.append(section)

    return ordered_sections
