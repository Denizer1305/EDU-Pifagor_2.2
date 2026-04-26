from __future__ import annotations

from django.db.models import Count, Prefetch, Q, QuerySet

from apps.assignments.models import Rubric, RubricCriterion


def get_rubric_base_queryset() -> QuerySet[Rubric]:
    return (
        Rubric.objects.select_related(
            "organization",
            "author",
        )
        .annotate(criteria_count=Count("criteria", distinct=True))
        .order_by("title", "id")
    )


def get_rubric_detail_queryset() -> QuerySet[Rubric]:
    return get_rubric_base_queryset().prefetch_related(
        Prefetch(
            "criteria",
            queryset=RubricCriterion.objects.order_by("order", "id"),
        )
    )


def get_rubrics_queryset(
    *,
    search: str = "",
    assignment_kind: str = "",
    organization_id: int | None = None,
    author_id: int | None = None,
    is_template: bool | None = None,
    is_active: bool | None = None,
) -> QuerySet[Rubric]:
    queryset = get_rubric_base_queryset()

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(assignment_kind__icontains=search)
            | Q(author__email__icontains=search)
            | Q(organization__name__icontains=search)
        )

    if assignment_kind:
        queryset = queryset.filter(assignment_kind=assignment_kind)

    if organization_id:
        queryset = queryset.filter(organization_id=organization_id)

    if author_id:
        queryset = queryset.filter(author_id=author_id)

    if is_template is not None:
        queryset = queryset.filter(is_template=is_template)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset


def get_rubric_by_id(*, rubric_id: int) -> Rubric | None:
    return get_rubric_detail_queryset().filter(id=rubric_id).first()


def get_rubric_criteria_queryset(
    *,
    rubric_id: int | None = None,
    criterion_type: str = "",
) -> QuerySet[RubricCriterion]:
    queryset = (
        RubricCriterion.objects.select_related("rubric")
        .order_by("order", "id")
    )

    if rubric_id:
        queryset = queryset.filter(rubric_id=rubric_id)

    if criterion_type:
        queryset = queryset.filter(criterion_type=criterion_type)

    return queryset
