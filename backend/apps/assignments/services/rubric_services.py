from __future__ import annotations

from django.db import transaction

from apps.assignments.models import Rubric, RubricCriterion


@transaction.atomic
def create_rubric(
    *,
    title: str,
    description: str = "",
    assignment_kind: str = "",
    organization=None,
    author=None,
    is_template: bool = True,
    is_active: bool = True,
) -> Rubric:
    rubric = Rubric(
        title=title,
        description=description,
        assignment_kind=assignment_kind,
        organization=organization,
        author=author,
        is_template=is_template,
        is_active=is_active,
    )
    rubric.full_clean()
    rubric.save()
    return rubric


@transaction.atomic
def update_rubric(rubric: Rubric, **fields) -> Rubric:
    for field_name, value in fields.items():
        setattr(rubric, field_name, value)

    rubric.full_clean()
    rubric.save()
    return rubric


@transaction.atomic
def create_rubric_criterion(
    *,
    rubric: Rubric,
    title: str,
    description: str = "",
    max_score=0,
    order: int = 1,
    criterion_type: str = RubricCriterion.CriterionTypeChoices.SCORE,
) -> RubricCriterion:
    criterion = RubricCriterion(
        rubric=rubric,
        title=title,
        description=description,
        max_score=max_score,
        order=order,
        criterion_type=criterion_type,
    )
    criterion.full_clean()
    criterion.save()
    return criterion


@transaction.atomic
def update_rubric_criterion(
    criterion: RubricCriterion,
    **fields,
) -> RubricCriterion:
    for field_name, value in fields.items():
        setattr(criterion, field_name, value)

    criterion.full_clean()
    criterion.save()
    return criterion


@transaction.atomic
def delete_rubric_criterion(criterion: RubricCriterion) -> None:
    criterion.delete()


@transaction.atomic
def reorder_rubric_criteria(
    *,
    rubric: Rubric,
    criterion_ids_in_order: list[int],
) -> list[RubricCriterion]:
    criteria = list(rubric.criteria.filter(id__in=criterion_ids_in_order))
    criteria_map = {criterion.id: criterion for criterion in criteria}

    ordered: list[RubricCriterion] = []
    for index, criterion_id in enumerate(criterion_ids_in_order, start=1):
        criterion = criteria_map.get(criterion_id)
        if criterion is None:
            continue
        criterion.order = index
        criterion.full_clean()
        criterion.save(update_fields=("order", "updated_at"))
        ordered.append(criterion)

    return ordered
