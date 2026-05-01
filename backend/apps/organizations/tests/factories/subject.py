from __future__ import annotations

from apps.organizations.models import Subject, SubjectCategory
from apps.organizations.tests.factories.counters import (
    subject_category_counter,
    subject_counter,
)


def create_subject_category(
    *,
    code: str | None = None,
    name: str | None = None,
    description: str = "",
    is_active: bool = True,
):
    """Создаёт тестовую категорию предметов."""

    index = next(subject_category_counter)

    if code is None:
        code = f"subject_category_{index}"

    if name is None:
        name = f"Категория предметов {index}"

    return SubjectCategory.objects.create(
        code=code,
        name=name,
        description=description,
        is_active=is_active,
    )


def create_subject(
    *,
    category=None,
    name: str | None = None,
    short_name: str | None = None,
    description: str = "",
    is_active: bool = True,
):
    """Создаёт тестовый предмет."""

    index = next(subject_counter)

    if category is None:
        category = create_subject_category()

    if name is None:
        name = f"Предмет {index}"

    if short_name is None:
        short_name = f"Предмет {index}"

    return Subject.objects.create(
        category=category,
        name=name,
        short_name=short_name,
        description=description,
        is_active=is_active,
    )
