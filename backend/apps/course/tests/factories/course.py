from __future__ import annotations

from apps.course.models import Course, CourseTeacher
from apps.course.tests.factories.common import (
    _unwrap_factory_result,
    course_counter,
)
from apps.course.tests.factories.context import (
    create_academic_year,
    create_education_period,
    create_group,
    create_group_subject,
    create_organization,
    create_subject,
)
from apps.course.tests.factories.users import create_course_author


def create_course(
    *,
    author=None,
    title: str | None = None,
    subtitle: str = "",
    description: str = "",
    course_type: str = Course.CourseTypeChoices.AUTHOR,
    origin: str = Course.OriginChoices.MANUAL,
    status: str = Course.StatusChoices.DRAFT,
    visibility: str = Course.VisibilityChoices.ASSIGNED_ONLY,
    level: str = Course.LevelChoices.BASIC,
    language: str = "ru",
    organization=None,
    subject=None,
    academic_year=None,
    period=None,
    group_subject=None,
    cover_image=None,
    is_template: bool = False,
    is_active: bool = True,
    allow_self_enrollment: bool = False,
    enrollment_code: str | None = None,
    estimated_minutes: int = 0,
    starts_at=None,
    ends_at=None,
    create_owner_link: bool = True,
):
    """Создаёт тестовый курс."""

    index = next(course_counter)

    if author is None:
        author = create_course_author()

    author = _unwrap_factory_result(author)

    if title is None:
        title = f"Курс {index}"

    course = Course(
        title=title,
        subtitle=subtitle,
        description=description,
        course_type=course_type,
        origin=origin,
        status=status,
        visibility=visibility,
        level=level,
        language=language,
        author=author,
        organization=organization,
        subject=subject,
        academic_year=academic_year,
        period=period,
        group_subject=group_subject,
        cover_image=cover_image,
        is_template=is_template,
        is_active=is_active,
        allow_self_enrollment=allow_self_enrollment,
        enrollment_code=enrollment_code,
        estimated_minutes=estimated_minutes,
        starts_at=starts_at,
        ends_at=ends_at,
    )
    course.full_clean()
    course.save()

    if create_owner_link:
        CourseTeacher.objects.create(
            course=course,
            teacher=author,
            role=CourseTeacher.RoleChoices.OWNER,
            is_active=True,
            can_edit=True,
            can_manage_structure=True,
            can_manage_assignments=True,
            can_view_analytics=True,
        )

    return course


def create_course_with_context(*, author=None, title: str | None = None):
    """Создаёт курс вместе с организационным и учебным контекстом."""

    organization = create_organization()
    subject = create_subject()
    academic_year = create_academic_year()
    period = create_education_period(academic_year=academic_year)
    group = create_group(organization=organization)
    group_subject = create_group_subject(
        group=group,
        subject=subject,
        academic_year=academic_year,
        period=period,
    )

    course = create_course(
        author=author,
        title=title,
        organization=organization,
        subject=subject,
        academic_year=academic_year,
        period=period,
        group_subject=group_subject,
    )

    return {
        "course": course,
        "organization": organization,
        "subject": subject,
        "academic_year": academic_year,
        "period": period,
        "group": group,
        "group_subject": group_subject,
    }
