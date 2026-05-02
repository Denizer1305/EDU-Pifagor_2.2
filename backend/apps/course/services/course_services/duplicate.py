from __future__ import annotations

from django.db import transaction

from apps.course.models import (
    Course,
    CourseLesson,
    CourseMaterial,
    CourseModule,
    CourseTeacher,
)
from apps.course.models.base import normalize_text
from apps.course.services.course_services.recalculation import (
    _recalculate_course_estimated_minutes,
)


def _copy_course_teachers(
    *,
    source_course: Course,
    new_course: Course,
    author,
    duplicate_teachers: bool,
) -> None:
    """Создаёт владельца курса и при необходимости копирует остальных преподавателей."""

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

    if not duplicate_teachers:
        return

    for teacher_link in source_course.course_teachers.filter(is_active=True).exclude(
        teacher=author,
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


def _copy_course_modules(
    *,
    source_course: Course,
    new_course: Course,
) -> dict[int, CourseModule]:
    """Копирует модули курса и возвращает карту old_id -> new_module."""

    module_map: dict[int, CourseModule] = {}

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

    return module_map


def _copy_course_lessons(
    *,
    source_course: Course,
    new_course: Course,
    module_map: dict[int, CourseModule],
) -> dict[int, CourseLesson]:
    """Копирует уроки курса и возвращает карту old_id -> new_lesson."""

    lesson_map: dict[int, CourseLesson] = {}

    for lesson in source_course.lessons.all().order_by(
        "module__order",
        "order",
        "id",
    ):
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

    return lesson_map


def _copy_course_root_materials(
    *,
    source_course: Course,
    new_course: Course,
) -> None:
    """Копирует материалы курса, не привязанные к урокам."""

    for material in source_course.materials.filter(lesson__isnull=True).order_by(
        "order",
        "id",
    ):
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


def _copy_course_lesson_materials(
    *,
    source_course: Course,
    new_course: Course,
    lesson_map: dict[int, CourseLesson],
) -> None:
    """Копирует материалы, привязанные к урокам."""

    for material in CourseMaterial.objects.filter(
        course=source_course,
        lesson__isnull=False,
    ).order_by(
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


@transaction.atomic
def duplicate_course(
    *,
    source_course: Course,
    author,
    title: str | None = None,
    duplicate_teachers: bool = False,
    duplicate_materials: bool = True,
) -> Course:
    """Создаёт копию курса вместе со структурой."""

    new_course = Course.objects.create(
        title=normalize_text(title) or f"{source_course.title} (копия)",
        subtitle=source_course.subtitle,
        description=source_course.description,
        course_type=source_course.course_type,
        origin=(
            Course.OriginChoices.TEMPLATE
            if source_course.is_template
            else source_course.origin
        ),
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
        cover_image=source_course.cover_image.name
        if source_course.cover_image
        else None,
        is_template=False,
        is_active=True,
        allow_self_enrollment=False,
        enrollment_code=None,
        estimated_minutes=0,
        starts_at=None,
        ends_at=None,
    )

    _copy_course_teachers(
        source_course=source_course,
        new_course=new_course,
        author=author,
        duplicate_teachers=duplicate_teachers,
    )

    module_map = _copy_course_modules(
        source_course=source_course,
        new_course=new_course,
    )
    lesson_map = _copy_course_lessons(
        source_course=source_course,
        new_course=new_course,
        module_map=module_map,
    )

    if duplicate_materials:
        _copy_course_root_materials(
            source_course=source_course,
            new_course=new_course,
        )
        _copy_course_lesson_materials(
            source_course=source_course,
            new_course=new_course,
            lesson_map=lesson_map,
        )

    return _recalculate_course_estimated_minutes(new_course)
