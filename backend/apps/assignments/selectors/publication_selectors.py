from __future__ import annotations

from django.apps import apps
from django.db.models import Count, Prefetch, Q, QuerySet
from django.utils import timezone

from apps.assignments.models import AssignmentAudience, AssignmentPublication


def get_assignment_publication_base_queryset() -> QuerySet[AssignmentPublication]:
    return (
        AssignmentPublication.objects.select_related(
            "assignment",
            "course",
            "lesson",
            "published_by",
            "assignment__author",
            "assignment__subject",
            "assignment__organization",
        )
        .annotate(
            audiences_count=Count("audiences", distinct=True),
            submissions_count=Count("submissions", distinct=True),
        )
        .order_by("-created_at")
    )


def get_assignment_publication_detail_queryset() -> QuerySet[AssignmentPublication]:
    return get_assignment_publication_base_queryset().prefetch_related(
        Prefetch(
            "audiences",
            queryset=AssignmentAudience.objects.select_related(
                "group",
                "student",
                "course_enrollment",
            ).order_by("-created_at"),
        ),
        "assignment__policy",
        "assignment__official_format",
        "assignment__variants",
    )


def get_assignment_publications_queryset(
    *,
    search: str = "",
    status: str = "",
    assignment_id: int | None = None,
    course_id: int | None = None,
    lesson_id: int | None = None,
    published_by_id: int | None = None,
    is_active: bool | None = None,
    starts_from=None,
    starts_to=None,
    due_from=None,
    due_to=None,
) -> QuerySet[AssignmentPublication]:
    queryset = get_assignment_publication_base_queryset()

    if search:
        queryset = queryset.filter(
            Q(assignment__title__icontains=search)
            | Q(title_override__icontains=search)
            | Q(notes__icontains=search)
            | Q(course__title__icontains=search)
            | Q(lesson__title__icontains=search)
            | Q(published_by__email__icontains=search)
        )

    if status:
        queryset = queryset.filter(status=status)

    if assignment_id:
        queryset = queryset.filter(assignment_id=assignment_id)

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if lesson_id:
        queryset = queryset.filter(lesson_id=lesson_id)

    if published_by_id:
        queryset = queryset.filter(published_by_id=published_by_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if starts_from:
        queryset = queryset.filter(starts_at__gte=starts_from)

    if starts_to:
        queryset = queryset.filter(starts_at__lte=starts_to)

    if due_from:
        queryset = queryset.filter(due_at__gte=due_from)

    if due_to:
        queryset = queryset.filter(due_at__lte=due_to)

    return queryset


def get_assignment_publication_by_id(
    *, publication_id: int
) -> AssignmentPublication | None:
    return (
        get_assignment_publication_detail_queryset().filter(id=publication_id).first()
    )


def get_available_publications_for_student_queryset(
    *,
    student,
    course_id: int | None = None,
    lesson_id: int | None = None,
) -> QuerySet[AssignmentPublication]:
    now = timezone.now()

    CourseEnrollment = apps.get_model("course", "CourseEnrollment")
    StudentGroupEnrollment = apps.get_model("education", "StudentGroupEnrollment")

    course_ids = list(
        CourseEnrollment.objects.filter(student=student).values_list(
            "course_id", flat=True
        )
    )
    group_ids = list(
        StudentGroupEnrollment.objects.filter(student=student).values_list(
            "group_id", flat=True
        )
    )

    queryset = (
        get_assignment_publication_base_queryset()
        .filter(
            status=AssignmentPublication.StatusChoices.PUBLISHED,
            is_active=True,
        )
        .filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
        )
        .filter(
            Q(available_until__isnull=True) | Q(available_until__gte=now),
        )
        .filter(
            Q(
                audiences__audience_type=AssignmentAudience.AudienceTypeChoices.ALL_COURSE_STUDENTS,
                course_id__in=course_ids,
            )
            | Q(
                audiences__audience_type=AssignmentAudience.AudienceTypeChoices.GROUP,
                audiences__group_id__in=group_ids,
            )
            | Q(
                audiences__audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
                audiences__student=student,
            )
            | Q(
                audiences__audience_type=AssignmentAudience.AudienceTypeChoices.SELECTED_STUDENTS,
                audiences__student=student,
            )
            | Q(audiences__course_enrollment__student=student)
        )
        .distinct()
    )

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if lesson_id:
        queryset = queryset.filter(lesson_id=lesson_id)

    return queryset
