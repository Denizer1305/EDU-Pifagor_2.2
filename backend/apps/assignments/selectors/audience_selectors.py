from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.assignments.models import AssignmentAudience


def get_assignment_audience_base_queryset() -> QuerySet[AssignmentAudience]:
    return (
        AssignmentAudience.objects.select_related(
            "publication",
            "publication__assignment",
            "publication__course",
            "publication__lesson",
            "group",
            "student",
            "course_enrollment",
        )
        .order_by("-created_at")
    )


def get_assignment_audiences_queryset(
    *,
    search: str = "",
    publication_id: int | None = None,
    audience_type: str = "",
    group_id: int | None = None,
    student_id: int | None = None,
    course_enrollment_id: int | None = None,
    is_active: bool | None = None,
) -> QuerySet[AssignmentAudience]:
    queryset = get_assignment_audience_base_queryset()

    if search:
        queryset = queryset.filter(
            Q(publication__assignment__title__icontains=search)
            | Q(publication__title_override__icontains=search)
            | Q(group__name__icontains=search)
            | Q(group__code__icontains=search)
            | Q(student__email__icontains=search)
            | Q(student__profile__last_name__icontains=search)
            | Q(student__profile__first_name__icontains=search)
        )

    if publication_id:
        queryset = queryset.filter(publication_id=publication_id)

    if audience_type:
        queryset = queryset.filter(audience_type=audience_type)

    if group_id:
        queryset = queryset.filter(group_id=group_id)

    if student_id:
        queryset = queryset.filter(student_id=student_id)

    if course_enrollment_id:
        queryset = queryset.filter(course_enrollment_id=course_enrollment_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset


def get_assignment_audience_by_id(*, audience_id: int) -> AssignmentAudience | None:
    return get_assignment_audience_base_queryset().filter(id=audience_id).first()


def get_publication_group_audiences_queryset(
    *,
    publication_id: int,
    is_active: bool | None = True,
) -> QuerySet[AssignmentAudience]:
    queryset = get_assignment_audiences_queryset(
        publication_id=publication_id,
        audience_type=AssignmentAudience.AudienceTypeChoices.GROUP,
        is_active=is_active,
    )
    return queryset


def get_publication_student_audiences_queryset(
    *,
    publication_id: int,
    is_active: bool | None = True,
) -> QuerySet[AssignmentAudience]:
    queryset = get_assignment_audiences_queryset(
        publication_id=publication_id,
        is_active=is_active,
    ).filter(
        audience_type__in=(
            AssignmentAudience.AudienceTypeChoices.STUDENT,
            AssignmentAudience.AudienceTypeChoices.SELECTED_STUDENTS,
        )
    )
    return queryset
