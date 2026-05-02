from __future__ import annotations

from django.db.models import Count, Prefetch, Q, QuerySet

from apps.assignments.models import (
    Assignment,
    AssignmentAttachment,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
)


def get_assignment_base_queryset() -> QuerySet[Assignment]:
    return (
        Assignment.objects.select_related(
            "course",
            "lesson",
            "subject",
            "organization",
            "author",
        )
        .annotate(
            variants_count=Count("variants", distinct=True),
            sections_count=Count("sections", distinct=True),
            questions_count=Count("questions", distinct=True),
            publications_count=Count("publications", distinct=True),
        )
        .order_by("-created_at")
    )


def get_assignment_detail_queryset() -> QuerySet[Assignment]:
    return get_assignment_base_queryset().prefetch_related(
        Prefetch(
            "variants",
            queryset=AssignmentVariant.objects.order_by(
                "order", "variant_number", "id"
            ),
        ),
        Prefetch(
            "sections",
            queryset=AssignmentSection.objects.select_related("variant").order_by(
                "order", "id"
            ),
        ),
        Prefetch(
            "questions",
            queryset=AssignmentQuestion.objects.select_related(
                "variant", "section"
            ).order_by("order", "id"),
        ),
        Prefetch(
            "attachments",
            queryset=AssignmentAttachment.objects.select_related("variant").order_by(
                "order", "id"
            ),
        ),
        "policy",
        "official_format",
    )


def get_assignments_queryset(
    *,
    search: str = "",
    status: str = "",
    assignment_kind: str = "",
    control_scope: str = "",
    education_level: str = "",
    course_id: int | None = None,
    lesson_id: int | None = None,
    subject_id: int | None = None,
    organization_id: int | None = None,
    author_id: int | None = None,
    is_template: bool | None = None,
    is_active: bool | None = None,
) -> QuerySet[Assignment]:
    queryset = get_assignment_base_queryset()

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(subtitle__icontains=search)
            | Q(description__icontains=search)
            | Q(instructions__icontains=search)
            | Q(author__email__icontains=search)
            | Q(author__profile__last_name__icontains=search)
            | Q(author__profile__first_name__icontains=search)
            | Q(subject__name__icontains=search)
            | Q(organization__name__icontains=search)
        )

    if status:
        queryset = queryset.filter(status=status)

    if assignment_kind:
        queryset = queryset.filter(assignment_kind=assignment_kind)

    if control_scope:
        queryset = queryset.filter(control_scope=control_scope)

    if education_level:
        queryset = queryset.filter(education_level=education_level)

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if lesson_id:
        queryset = queryset.filter(lesson_id=lesson_id)

    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)

    if organization_id:
        queryset = queryset.filter(organization_id=organization_id)

    if author_id:
        queryset = queryset.filter(author_id=author_id)

    if is_template is not None:
        queryset = queryset.filter(is_template=is_template)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset


def get_teacher_assignments_queryset(
    *,
    teacher,
    search: str = "",
    status: str = "",
    assignment_kind: str = "",
    course_id: int | None = None,
    lesson_id: int | None = None,
    is_active: bool | None = None,
) -> QuerySet[Assignment]:
    queryset = get_assignments_queryset(
        search=search,
        status=status,
        assignment_kind=assignment_kind,
        course_id=course_id,
        lesson_id=lesson_id,
        author_id=teacher.id,
        is_active=is_active,
    )
    return queryset


def get_assignment_by_id(*, assignment_id: int) -> Assignment | None:
    return get_assignment_detail_queryset().filter(id=assignment_id).first()


def get_assignment_variants_queryset(
    *, assignment_id: int | None = None
) -> QuerySet[AssignmentVariant]:
    queryset = AssignmentVariant.objects.select_related("assignment").order_by(
        "order", "variant_number", "id"
    )
    if assignment_id:
        queryset = queryset.filter(assignment_id=assignment_id)
    return queryset


def get_assignment_sections_queryset(
    *,
    assignment_id: int | None = None,
    variant_id: int | None = None,
) -> QuerySet[AssignmentSection]:
    queryset = AssignmentSection.objects.select_related(
        "assignment", "variant"
    ).order_by("order", "id")
    if assignment_id:
        queryset = queryset.filter(assignment_id=assignment_id)
    if variant_id:
        queryset = queryset.filter(variant_id=variant_id)
    return queryset


def get_assignment_questions_queryset(
    *,
    assignment_id: int | None = None,
    variant_id: int | None = None,
    section_id: int | None = None,
    question_type: str = "",
) -> QuerySet[AssignmentQuestion]:
    queryset = AssignmentQuestion.objects.select_related(
        "assignment", "variant", "section"
    ).order_by("order", "id")

    if assignment_id:
        queryset = queryset.filter(assignment_id=assignment_id)

    if variant_id:
        queryset = queryset.filter(variant_id=variant_id)

    if section_id:
        queryset = queryset.filter(section_id=section_id)

    if question_type:
        queryset = queryset.filter(question_type=question_type)

    return queryset
