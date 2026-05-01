from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import Course, CourseLesson, CourseMaterial
from apps.course.models.base import normalize_text
from apps.course.services.course_structure_services.ordering import (
    _get_next_material_order,
)


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
    """Создаёт материал курса или урока."""

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
    """Обновляет материал курса или урока."""

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
    """Удаляет материал курса или урока."""

    material.delete()
