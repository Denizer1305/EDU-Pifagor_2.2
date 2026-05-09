from __future__ import annotations

from apps.course.models import CourseLesson, CourseMaterial, CourseModule
from apps.course.tests.factories.common import (
    create_course_file,
    lesson_counter,
    material_counter,
    module_counter,
)
from apps.course.tests.factories.course import create_course


def create_course_module(
    *,
    course=None,
    title: str | None = None,
    description: str = "",
    order: int | None = None,
    is_required: bool = True,
    is_published: bool = True,
    estimated_minutes: int = 0,
):
    """Создаёт тестовый модуль курса."""

    index = next(module_counter)

    if course is None:
        course = create_course()

    if title is None:
        title = f"Модуль {index}"

    if order is None:
        last_module = course.modules.order_by("-order", "-id").first()
        order = (last_module.order if last_module else 0) + 1

    module = CourseModule(
        course=course,
        title=title,
        description=description,
        order=order,
        is_required=is_required,
        is_published=is_published,
        estimated_minutes=estimated_minutes,
    )
    module.full_clean()
    module.save()
    return module


def create_course_lesson(
    *,
    course=None,
    module=None,
    title: str | None = None,
    subtitle: str = "",
    description: str = "",
    content: str = "",
    lesson_type: str = CourseLesson.LessonTypeChoices.TEXT,
    order: int | None = None,
    estimated_minutes: int = 15,
    is_required: bool = True,
    is_preview: bool = False,
    is_published: bool = True,
    available_from=None,
    video_url: str = "",
    external_url: str = "",
):
    """Создаёт тестовый урок курса."""

    index = next(lesson_counter)

    if course is None and module is None:
        course = create_course()
        module = create_course_module(course=course)

    if course is None:
        course = module.course

    if module is None:
        module = create_course_module(course=course)

    if title is None:
        title = f"Урок {index}"

    if order is None:
        last_lesson = module.lessons.order_by("-order", "-id").first()
        order = (last_lesson.order if last_lesson else 0) + 1

    lesson = CourseLesson(
        course=course,
        module=module,
        title=title,
        subtitle=subtitle,
        description=description,
        content=content,
        lesson_type=lesson_type,
        order=order,
        estimated_minutes=estimated_minutes,
        is_required=is_required,
        is_preview=is_preview,
        is_published=is_published,
        available_from=available_from,
        video_url=video_url,
        external_url=external_url,
    )
    lesson.full_clean()
    lesson.save()
    return lesson


def create_course_material(
    *,
    course=None,
    lesson=None,
    title: str | None = None,
    description: str = "",
    material_type: str = CourseMaterial.MaterialTypeChoices.FILE,
    file=None,
    external_url: str = "",
    order: int | None = None,
    is_downloadable: bool = True,
    is_visible: bool = True,
):
    """Создаёт тестовый материал курса или урока."""

    index = next(material_counter)

    if course is None and lesson is None:
        lesson = create_course_lesson()

    if lesson is not None and course is None:
        course = lesson.course

    if course is None:
        course = create_course()

    if title is None:
        title = f"Материал {index}"

    if order is None:
        last_item = (
            CourseMaterial.objects.filter(
                course=course,
                lesson=lesson,
            )
            .order_by("-order", "-id")
            .first()
        )
        order = (last_item.order if last_item else 0) + 1

    if file is None and material_type != CourseMaterial.MaterialTypeChoices.LINK:
        file = create_course_file()

    material = CourseMaterial(
        course=course,
        lesson=lesson,
        title=title,
        description=description,
        material_type=material_type,
        file=file,
        external_url=external_url,
        order=order,
        is_downloadable=is_downloadable,
        is_visible=is_visible,
    )
    material.full_clean()
    material.save()
    return material
