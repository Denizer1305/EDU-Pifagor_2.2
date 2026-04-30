from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import (
    Course,
    CourseLesson,
    CourseMaterial,
    CourseModule,
    CourseTeacher,
)
from apps.course.models.base import build_unique_slug, generate_code, normalize_text


def _validate_course_can_be_published(course: Course) -> None:
    if not course.title:
        raise ValidationError({"title": "Нельзя публиковать курс без названия."})

    if not course.modules.exists():
        raise ValidationError(
            {"status": "Нельзя публиковать курс без модулей."}
        )

    has_published_lessons = course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).exists()
    if not has_published_lessons:
        raise ValidationError(
            {"status": "Нельзя публиковать курс без опубликованных уроков."}
        )


def _recalculate_course_estimated_minutes(course: Course) -> Course:
    estimated_minutes = (
        course.lessons.filter(
            is_published=True,
            module__is_published=True,
        )
        .values_list("estimated_minutes", flat=True)
    )
    total_minutes = sum(estimated_minutes) if estimated_minutes else 0

    if course.estimated_minutes != total_minutes:
        course.estimated_minutes = total_minutes
        course.full_clean()
        course.save(update_fields=["estimated_minutes", "updated_at"])

    return course


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


@transaction.atomic
def publish_course(*, course: Course) -> Course:
    _validate_course_can_be_published(course)
    course.status = Course.StatusChoices.PUBLISHED
    course.full_clean()
    course.save(update_fields=["status", "published_at", "updated_at"])
    return course


@transaction.atomic
def archive_course(*, course: Course) -> Course:
    course.status = Course.StatusChoices.ARCHIVED
    course.is_active = False
    course.full_clean()
    course.save(update_fields=["status", "is_active", "archived_at", "updated_at"])
    return course


@transaction.atomic
def add_teacher_to_course(
    *,
    course: Course,
    teacher,
    role: str = CourseTeacher.RoleChoices.TEACHER,
    is_active: bool = True,
    can_edit: bool = True,
    can_manage_structure: bool = True,
    can_manage_assignments: bool = False,
    can_view_analytics: bool = True,
) -> CourseTeacher:
    link, created = CourseTeacher.objects.get_or_create(
        course=course,
        teacher=teacher,
        defaults={
            "role": role,
            "is_active": is_active,
            "can_edit": can_edit,
            "can_manage_structure": can_manage_structure,
            "can_manage_assignments": can_manage_assignments,
            "can_view_analytics": can_view_analytics,
        },
    )

    if not created:
        link.role = role
        link.is_active = is_active
        link.can_edit = can_edit
        link.can_manage_structure = can_manage_structure
        link.can_manage_assignments = can_manage_assignments
        link.can_view_analytics = can_view_analytics
        link.full_clean()
        link.save(
            update_fields=[
                "role",
                "is_active",
                "can_edit",
                "can_manage_structure",
                "can_manage_assignments",
                "can_view_analytics",
                "updated_at",
            ]
        )

    return link


@transaction.atomic
def remove_teacher_from_course(*, course: Course, teacher) -> None:
    link = CourseTeacher.objects.filter(course=course, teacher=teacher).first()
    if not link:
        return

    if link.role == CourseTeacher.RoleChoices.OWNER:
        owners_count = CourseTeacher.objects.filter(
            course=course,
            role=CourseTeacher.RoleChoices.OWNER,
            is_active=True,
        ).count()
        if owners_count <= 1:
            raise ValidationError(
                {"teacher": "Нельзя удалить единственного владельца курса."}
            )

    link.is_active = False
    link.full_clean()
    link.save(update_fields=["is_active", "updated_at"])


@transaction.atomic
def duplicate_course(
    *,
    source_course: Course,
    author,
    title: str | None = None,
    duplicate_teachers: bool = False,
    duplicate_materials: bool = True,
) -> Course:
    new_course = Course.objects.create(
        title=normalize_text(title) or f"{source_course.title} (копия)",
        subtitle=source_course.subtitle,
        description=source_course.description,
        course_type=source_course.course_type,
        origin=Course.OriginChoices.TEMPLATE if source_course.is_template else source_course.origin,
        status=Course.StatusChoices.DRAFT,
        visibility=source_course.visibility,
        level=source_course.level,
        language=source_course.language,
        author=author,
        organization=source_course.organization,
        subject=source_course.subject,
        academic_year=source_course.academic_year,
        period=source_course.period,
        group_subject=source_course.group_subject,
        cover_image=source_course.cover_image.name if source_course.cover_image else None,
        is_template=False,
        is_active=True,
        allow_self_enrollment=False,
        enrollment_code=None,
        estimated_minutes=0,
        starts_at=None,
        ends_at=None,
    )

    CourseTeacher.objects.create(
        course=new_course,
        teacher=author,
        role=CourseTeacher.RoleChoices.OWNER,
        is_active=True,
        can_edit=True,
        can_manage_structure=True,
        can_manage_assignments=True,
        can_view_analytics=True,
    )

    if duplicate_teachers:
        for teacher_link in source_course.course_teachers.filter(is_active=True).exclude(
            teacher=author
        ):
            CourseTeacher.objects.create(
                course=new_course,
                teacher=teacher_link.teacher,
                role=teacher_link.role,
                is_active=teacher_link.is_active,
                can_edit=teacher_link.can_edit,
                can_manage_structure=teacher_link.can_manage_structure,
                can_manage_assignments=teacher_link.can_manage_assignments,
                can_view_analytics=teacher_link.can_view_analytics,
            )

    module_map: dict[int, CourseModule] = {}
    lesson_map: dict[int, CourseLesson] = {}

    for module in source_course.modules.all().order_by("order", "id"):
        new_module = CourseModule.objects.create(
            course=new_course,
            title=module.title,
            description=module.description,
            order=module.order,
            is_required=module.is_required,
            is_published=module.is_published,
            estimated_minutes=module.estimated_minutes,
        )
        module_map[module.id] = new_module

    for lesson in source_course.lessons.all().order_by("module__order", "order", "id"):
        new_lesson = CourseLesson.objects.create(
            course=new_course,
            module=module_map[lesson.module_id],
            title=lesson.title,
            subtitle=lesson.subtitle,
            description=lesson.description,
            content=lesson.content,
            lesson_type=lesson.lesson_type,
            order=lesson.order,
            estimated_minutes=lesson.estimated_minutes,
            is_required=lesson.is_required,
            is_preview=lesson.is_preview,
            is_published=lesson.is_published,
            available_from=None,
            video_url=lesson.video_url,
            external_url=lesson.external_url,
        )
        lesson_map[lesson.id] = new_lesson

    if duplicate_materials:
        for material in source_course.materials.filter(lesson__isnull=True).order_by("order", "id"):
            CourseMaterial.objects.create(
                course=new_course,
                lesson=None,
                title=material.title,
                description=material.description,
                material_type=material.material_type,
                file=material.file.name if material.file else None,
                external_url=material.external_url,
                order=material.order,
                is_downloadable=material.is_downloadable,
                is_visible=material.is_visible,
            )

        for material in CourseMaterial.objects.filter(course=source_course, lesson__isnull=False).order_by(
            "lesson__order",
            "order",
            "id",
        ):
            new_lesson = lesson_map.get(material.lesson_id)
            if not new_lesson:
                continue

            CourseMaterial.objects.create(
                course=new_course,
                lesson=new_lesson,
                title=material.title,
                description=material.description,
                material_type=material.material_type,
                file=material.file.name if material.file else None,
                external_url=material.external_url,
                order=material.order,
                is_downloadable=material.is_downloadable,
                is_visible=material.is_visible,
            )

    return _recalculate_course_estimated_minutes(new_course)
