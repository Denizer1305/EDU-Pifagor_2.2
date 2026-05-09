from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import Course, CourseModule
from apps.course.models.base import normalize_text
from apps.course.services.course_structure_services.ordering import (
    _get_next_module_order,
)
from apps.course.services.course_structure_services.recalculation import (
    _recalculate_course_estimated_minutes,
)


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
    """Создаёт модуль курса."""

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
    """Обновляет модуль курса."""

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
    """Удаляет модуль курса и пересчитывает длительность курса."""

    course = module.course
    module.delete()
    _recalculate_course_estimated_minutes(course)


@transaction.atomic
def reorder_course_modules(
    *,
    course: Course,
    module_ids_in_order: list[int],
) -> None:
    """Меняет порядок модулей курса."""

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
