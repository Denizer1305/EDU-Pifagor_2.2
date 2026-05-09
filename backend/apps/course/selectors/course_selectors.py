from __future__ import annotations

from django.db.models import Prefetch, Q

from apps.course.models import Course, CourseLesson, CourseModule


def get_courses_queryset(
    *,
    search: str = "",
    status: str = "",
    visibility: str = "",
    course_type: str = "",
    organization_id: int | None = None,
    subject_id: int | None = None,
    author_id: int | None = None,
    teacher_id: int | None = None,
    is_template: bool | None = None,
    is_active: bool | None = None,
):
    queryset = Course.objects.select_related(
        "author",
        "organization",
        "subject",
        "academic_year",
        "period",
        "group_subject",
    ).prefetch_related(
        "course_teachers",
    )

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(subtitle__icontains=search)
            | Q(description__icontains=search)
            | Q(code__icontains=search)
            | Q(slug__icontains=search)
            | Q(author__email__icontains=search)
            | Q(author__profile__first_name__icontains=search)
            | Q(author__profile__last_name__icontains=search)
            | Q(subject__name__icontains=search)
            | Q(organization__name__icontains=search)
        )

    if status:
        queryset = queryset.filter(status=status)

    if visibility:
        queryset = queryset.filter(visibility=visibility)

    if course_type:
        queryset = queryset.filter(course_type=course_type)

    if organization_id:
        queryset = queryset.filter(organization_id=organization_id)

    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)

    if author_id:
        queryset = queryset.filter(author_id=author_id)

    if teacher_id:
        queryset = queryset.filter(
            course_teachers__teacher_id=teacher_id,
            course_teachers__is_active=True,
        )

    if is_template is not None:
        queryset = queryset.filter(is_template=is_template)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.distinct().order_by("-created_at")


def get_course_detail_queryset():
    return Course.objects.select_related(
        "author",
        "organization",
        "subject",
        "academic_year",
        "period",
        "group_subject",
    ).prefetch_related(
        Prefetch(
            "modules",
            queryset=CourseModule.objects.order_by("order", "id"),
        ),
        Prefetch(
            "lessons",
            queryset=CourseLesson.objects.select_related("module").order_by(
                "module__order",
                "order",
                "id",
            ),
        ),
        "materials",
        "course_teachers__teacher",
    )


def get_course_by_id(*, course_id: int):
    return get_course_detail_queryset().filter(id=course_id).first()


def get_teacher_courses_queryset(
    *, teacher_id: int, status: str = "", search: str = ""
):
    return get_courses_queryset(
        teacher_id=teacher_id,
        status=status,
        search=search,
        is_active=True,
    )


def get_public_courses_queryset(
    *, search: str = "", organization_id: int | None = None
):
    queryset = get_courses_queryset(
        search=search,
        organization_id=organization_id,
        status=Course.StatusChoices.PUBLISHED,
        is_active=True,
    )
    return queryset.filter(
        visibility__in=[
            Course.VisibilityChoices.ORGANIZATION,
            Course.VisibilityChoices.PUBLIC_LINK,
        ]
    )
