from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import Course, CourseLesson, CourseMaterial, CourseModule
from apps.course.models.base import normalize_text


def _get_next_module_order(course: Course) -> int:
    last_module = course.modules.order_by("-order", "-id").first()
    return (last_module.order if last_module else 0) + 1


def _get_next_lesson_order(module: CourseModule) -> int:
    last_lesson = module.lessons.order_by("-order", "-id").first()
    return (last_lesson.order if last_lesson else 0) + 1


def _get_next_material_order(course: Course, lesson: CourseLesson | None = None) -> int:
    queryset = CourseMaterial.objects.filter(course=course, lesson=lesson).order_by("-order", "-id")
    last_item = queryset.first()
    return (last_item.order if last_item else 0) + 1


def _recalculate_module_estimated_minutes(module: CourseModule) -> CourseModule:
    minutes_values = module.lessons.values_list("estimated_minutes", flat=True)
    total_minutes = sum(minutes_values) if minutes_values else 0

    if module.estimated_minutes != total_minutes:
        module.estimated_minutes = total_minutes
        module.full_clean()
        module.save(update_fields=["estimated_minutes", "updated_at"])

    return module


def _recalculate_course_estimated_minutes(course: Course) -> Course:
    minutes_values = course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).values_list("estimated_minutes", flat=True)
    total_minutes = sum(minutes_values) if minutes_values else 0

    if course.estimated_minutes != total_minutes:
        course.estimated_minutes = total_minutes
        course.full_clean()
        course.save(update_fields=["estimated_minutes", "updated_at"])

    return course


@transaction.atomic
def create_course_module(
    *,
    course: Course,
    title: str,
    description: str = "",
    order: int | None = None,
    is_required: bool = True,
    is_published: bool = True,
) -> CourseModule:
    module = CourseModule(
        course=course,
        title=normalize_text(title),
        description=normalize_text(description),
        order=order or _get_next_module_order(course),
        is_required=is_required,
        is_published=is_published,
    )
    module.full_clean()
    module.save()
    return module


@transaction.atomic
def update_course_module(
    *,
    module: CourseModule,
    title: str | None = None,
    description: str | None = None,
    is_required: bool | None = None,
    is_published: bool | None = None,
) -> CourseModule:
    update_fields: list[str] = []

    if title is not None:
        module.title = normalize_text(title)
        update_fields.append("title")

    if description is not None:
        module.description = normalize_text(description)
        update_fields.append("description")

    if is_required is not None:
        module.is_required = is_required
        update_fields.append("is_required")

    if is_published is not None:
        module.is_published = is_published
        update_fields.append("is_published")

    module.full_clean()
    if update_fields:
        module.save(update_fields=[*update_fields, "updated_at"])

    _recalculate_course_estimated_minutes(module.course)
    return module


@transaction.atomic
def delete_course_module(*, module: CourseModule) -> None:
    course = module.course
    module.delete()
    _recalculate_course_estimated_minutes(course)


@transaction.atomic
def reorder_course_modules(*, course: Course, module_ids_in_order: list[int]) -> None:
    modules = list(course.modules.filter(id__in=module_ids_in_order))
    found_ids = {module.id for module in modules}
    requested_ids = set(module_ids_in_order)

    if found_ids != requested_ids:
        raise ValidationError(
            {"modules": "Список модулей содержит элементы, не принадлежащие курсу."}
        )

    module_map = {module.id: module for module in modules}
    temp_order_base = 100000

    for index, module_id in enumerate(module_ids_in_order, start=1):
        module = module_map[module_id]
        module.order = temp_order_base + index
        module.save(update_fields=["order", "updated_at"])

    for index, module_id in enumerate(module_ids_in_order, start=1):
        module = module_map[module_id]
        module.order = index
        module.full_clean()
        module.save(update_fields=["order", "updated_at"])


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


@transaction.atomic
def create_course_material(
    *,
    course: Course,
    lesson: CourseLesson | None = None,
    title: str,
    description: str = "",
    material_type: str = CourseMaterial.MaterialTypeChoices.FILE,
    file=None,
    external_url: str = "",
    order: int | None = None,
    is_downloadable: bool = True,
    is_visible: bool = True,
) -> CourseMaterial:
    if lesson and lesson.course_id != course.id:
        raise ValidationError({"lesson": "Урок не принадлежит выбранному курсу."})

    material = CourseMaterial(
        course=course,
        lesson=lesson,
        title=normalize_text(title),
        description=normalize_text(description),
        material_type=material_type,
        file=file,
        external_url=normalize_text(external_url),
        order=order or _get_next_material_order(course, lesson),
        is_downloadable=is_downloadable,
        is_visible=is_visible,
    )
    material.full_clean()
    material.save()
    return material


@transaction.atomic
def update_course_material(
    *,
    material: CourseMaterial,
    title: str | None = None,
    description: str | None = None,
    material_type: str | None = None,
    file=None,
    external_url: str | None = None,
    is_downloadable: bool | None = None,
    is_visible: bool | None = None,
) -> CourseMaterial:
    update_fields: list[str] = []

    if title is not None:
        material.title = normalize_text(title)
        update_fields.append("title")

    if description is not None:
        material.description = normalize_text(description)
        update_fields.append("description")

    if material_type is not None:
        material.material_type = material_type
        update_fields.append("material_type")

    if file is not None:
        material.file = file
        update_fields.append("file")

    if external_url is not None:
        material.external_url = normalize_text(external_url)
        update_fields.append("external_url")

    if is_downloadable is not None:
        material.is_downloadable = is_downloadable
        update_fields.append("is_downloadable")

    if is_visible is not None:
        material.is_visible = is_visible
        update_fields.append("is_visible")

    material.full_clean()
    if update_fields:
        material.save(update_fields=[*update_fields, "updated_at"])

    return material


@transaction.atomic
def delete_course_material(*, material: CourseMaterial) -> None:
    material.delete()
