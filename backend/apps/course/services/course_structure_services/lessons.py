from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import Course, CourseLesson, CourseModule
from apps.course.models.base import normalize_text
from apps.course.services.course_structure_services.ordering import (
    _get_next_lesson_order,
)
from apps.course.services.course_structure_services.recalculation import (
    _recalculate_course_estimated_minutes,
    _recalculate_module_estimated_minutes,
)


@transaction.atomic
def create_course_lesson(
    *,
    course: Course,
    module: CourseModule,
    title: str,
    subtitle: str = "",
    description: str = "",
    content: str = "",
    lesson_type: str = CourseLesson.LessonTypeChoices.TEXT,
    order: int | None = None,
    estimated_minutes: int = 0,
    is_required: bool = True,
    is_preview: bool = False,
    is_published: bool = True,
    available_from=None,
    video_url: str = "",
    external_url: str = "",
) -> CourseLesson:
    """Создаёт урок курса."""

    if module.course_id != course.id:
        raise ValidationError({"module": "Модуль не принадлежит указанному курсу."})

    lesson = CourseLesson(
        course=course,
        module=module,
        title=normalize_text(title),
        subtitle=normalize_text(subtitle),
        description=normalize_text(description),
        content=content or "",
        lesson_type=lesson_type,
        order=order or _get_next_lesson_order(module),
        estimated_minutes=max(0, estimated_minutes or 0),
        is_required=is_required,
        is_preview=is_preview,
        is_published=is_published,
        available_from=available_from,
        video_url=normalize_text(video_url),
        external_url=normalize_text(external_url),
    )
    lesson.full_clean()
    lesson.save()

    _recalculate_module_estimated_minutes(module)
    _recalculate_course_estimated_minutes(course)
    return lesson


@transaction.atomic
def update_course_lesson(
    *,
    lesson: CourseLesson,
    title: str | None = None,
    subtitle: str | None = None,
    description: str | None = None,
    content: str | None = None,
    lesson_type: str | None = None,
    estimated_minutes: int | None = None,
    is_required: bool | None = None,
    is_preview: bool | None = None,
    is_published: bool | None = None,
    available_from=None,
    video_url: str | None = None,
    external_url: str | None = None,
) -> CourseLesson:
    """Обновляет урок курса."""

    update_fields: list[str] = []

    if title is not None:
        lesson.title = normalize_text(title)
        update_fields.append("title")

    if subtitle is not None:
        lesson.subtitle = normalize_text(subtitle)
        update_fields.append("subtitle")

    if description is not None:
        lesson.description = normalize_text(description)
        update_fields.append("description")

    if content is not None:
        lesson.content = content
        update_fields.append("content")

    if lesson_type is not None:
        lesson.lesson_type = lesson_type
        update_fields.append("lesson_type")

    if estimated_minutes is not None:
        lesson.estimated_minutes = max(0, estimated_minutes or 0)
        update_fields.append("estimated_minutes")

    if is_required is not None:
        lesson.is_required = is_required
        update_fields.append("is_required")

    if is_preview is not None:
        lesson.is_preview = is_preview
        update_fields.append("is_preview")

    if is_published is not None:
        lesson.is_published = is_published
        update_fields.append("is_published")

    if available_from is not None:
        lesson.available_from = available_from
        update_fields.append("available_from")

    if video_url is not None:
        lesson.video_url = normalize_text(video_url)
        update_fields.append("video_url")

    if external_url is not None:
        lesson.external_url = normalize_text(external_url)
        update_fields.append("external_url")

    lesson.full_clean()
    if update_fields:
        lesson.save(update_fields=[*update_fields, "updated_at"])

    _recalculate_module_estimated_minutes(lesson.module)
    _recalculate_course_estimated_minutes(lesson.course)
    return lesson


@transaction.atomic
def delete_course_lesson(*, lesson: CourseLesson) -> None:
    """Удаляет урок курса и пересчитывает длительность модуля и курса."""

    course = lesson.course
    module = lesson.module
    lesson.delete()

    _recalculate_module_estimated_minutes(module)
    _recalculate_course_estimated_minutes(course)


@transaction.atomic
def move_course_lesson(
    *,
    lesson: CourseLesson,
    target_module: CourseModule,
    new_order: int | None = None,
) -> CourseLesson:
    """Перемещает урок в другой модуль того же курса."""

    if lesson.course_id != target_module.course_id:
        raise ValidationError(
            {"target_module": "Целевой модуль должен принадлежать тому же курсу."}
        )

    source_module = lesson.module
    lesson.module = target_module
    lesson.order = new_order or _get_next_lesson_order(target_module)
    lesson.full_clean()
    lesson.save(update_fields=["module", "order", "updated_at"])

    _recalculate_module_estimated_minutes(source_module)
    _recalculate_module_estimated_minutes(target_module)
    _recalculate_course_estimated_minutes(lesson.course)
    return lesson


@transaction.atomic
def reorder_course_lessons(
    *,
    module: CourseModule,
    lesson_ids_in_order: list[int],
) -> None:
    """Меняет порядок уроков внутри модуля."""

    lessons = list(module.lessons.filter(id__in=lesson_ids_in_order))
    found_ids = {lesson.id for lesson in lessons}
    requested_ids = set(lesson_ids_in_order)

    if found_ids != requested_ids:
        raise ValidationError(
            {"lessons": "Список уроков содержит элементы, не принадлежащие модулю."}
        )

    lesson_map = {lesson.id: lesson for lesson in lessons}
    temp_order_base = 100000

    for index, lesson_id in enumerate(lesson_ids_in_order, start=1):
        lesson = lesson_map[lesson_id]
        lesson.order = temp_order_base + index
        lesson.save(update_fields=["order", "updated_at"])

    for index, lesson_id in enumerate(lesson_ids_in_order, start=1):
        lesson = lesson_map[lesson_id]
        lesson.order = index
        lesson.full_clean()
        lesson.save(update_fields=["order", "updated_at"])
