from __future__ import annotations

from django.db import transaction

from apps.course.models import Course, CourseTeacher
from apps.course.models.base import (
    build_unique_slug,
    generate_code,
    normalize_text,
)


@transaction.atomic
def create_course(
    *,
    author,
    title: str,
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
) -> Course:
    """Создаёт курс и назначает автора владельцем курса."""

    course = Course(
        title=normalize_text(title),
        subtitle=normalize_text(subtitle),
        description=normalize_text(description),
        course_type=course_type,
        origin=origin,
        status=status,
        visibility=visibility,
        level=level,
        language=normalize_text(language) or "ru",
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
        enrollment_code=normalize_text(enrollment_code) or None,
        estimated_minutes=max(0, estimated_minutes or 0),
        starts_at=starts_at,
        ends_at=ends_at,
    )
    course.full_clean()
    course.save()

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


@transaction.atomic
def update_course(
    *,
    course: Course,
    title: str | None = None,
    subtitle: str | None = None,
    description: str | None = None,
    course_type: str | None = None,
    origin: str | None = None,
    status: str | None = None,
    visibility: str | None = None,
    level: str | None = None,
    language: str | None = None,
    organization=None,
    subject=None,
    academic_year=None,
    period=None,
    group_subject=None,
    cover_image=None,
    is_template: bool | None = None,
    is_active: bool | None = None,
    allow_self_enrollment: bool | None = None,
    enrollment_code: str | None = None,
    estimated_minutes: int | None = None,
    starts_at=None,
    ends_at=None,
) -> Course:
    """Обновляет курс.

    Поведение сохранено как в старом файле: поля со значением None не обновляются.
    """

    update_fields: list[str] = []

    if title is not None:
        course.title = normalize_text(title)
        course.slug = build_unique_slug(
            Course,
            course.title or course.code or generate_code("CRS"),
            instance=course,
        )
        update_fields.extend(["title", "slug"])

    if subtitle is not None:
        course.subtitle = normalize_text(subtitle)
        update_fields.append("subtitle")

    if description is not None:
        course.description = normalize_text(description)
        update_fields.append("description")

    if course_type is not None:
        course.course_type = course_type
        update_fields.append("course_type")

    if origin is not None:
        course.origin = origin
        update_fields.append("origin")

    if status is not None:
        course.status = status
        update_fields.append("status")

    if visibility is not None:
        course.visibility = visibility
        update_fields.append("visibility")

    if level is not None:
        course.level = level
        update_fields.append("level")

    if language is not None:
        course.language = normalize_text(language) or "ru"
        update_fields.append("language")

    if organization is not None:
        course.organization = organization
        update_fields.append("organization")

    if subject is not None:
        course.subject = subject
        update_fields.append("subject")

    if academic_year is not None:
        course.academic_year = academic_year
        update_fields.append("academic_year")

    if period is not None:
        course.period = period
        update_fields.append("period")

    if group_subject is not None:
        course.group_subject = group_subject
        update_fields.append("group_subject")

    if cover_image is not None:
        course.cover_image = cover_image
        update_fields.append("cover_image")

    if is_template is not None:
        course.is_template = is_template
        update_fields.append("is_template")

    if is_active is not None:
        course.is_active = is_active
        update_fields.append("is_active")

    if allow_self_enrollment is not None:
        course.allow_self_enrollment = allow_self_enrollment
        update_fields.append("allow_self_enrollment")

    if enrollment_code is not None:
        course.enrollment_code = normalize_text(enrollment_code) or None
        update_fields.append("enrollment_code")

    if estimated_minutes is not None:
        course.estimated_minutes = max(0, estimated_minutes or 0)
        update_fields.append("estimated_minutes")

    if starts_at is not None:
        course.starts_at = starts_at
        update_fields.append("starts_at")

    if ends_at is not None:
        course.ends_at = ends_at
        update_fields.append("ends_at")

    course.full_clean()

    if update_fields:
        course.save(update_fields=[*update_fields, "updated_at"])

    return course
