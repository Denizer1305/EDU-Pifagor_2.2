from __future__ import annotations

from apps.course.tests.factories.common import _unwrap_factory_result
from apps.education.tests.factories import (
    create_academic_year as base_create_academic_year,
)
from apps.education.tests.factories import (
    create_education_period as base_create_education_period,
)
from apps.education.tests.factories import (
    create_group_subject as base_create_group_subject,
)
from apps.organizations.tests.factories import (
    create_group as base_create_group,
)
from apps.organizations.tests.factories import (
    create_organization as base_create_organization,
)
from apps.organizations.tests.factories import (
    create_subject as base_create_subject,
)


def create_organization():
    """Создаёт тестовую организацию."""

    return _unwrap_factory_result(base_create_organization())


def create_subject():
    """Создаёт тестовый предмет."""

    return _unwrap_factory_result(base_create_subject())


def create_group(*, organization=None):
    """Создаёт тестовую учебную группу."""

    return _unwrap_factory_result(base_create_group(organization=organization))


def create_academic_year():
    """Создаёт тестовый учебный год."""

    return _unwrap_factory_result(base_create_academic_year())


def create_education_period(*, academic_year=None):
    """Создаёт тестовый учебный период."""

    return _unwrap_factory_result(
        base_create_education_period(academic_year=academic_year)
    )


def create_group_subject(*, group=None, subject=None, academic_year=None, period=None):
    """Создаёт тестовую связь группы, предмета и учебного периода."""

    return _unwrap_factory_result(
        base_create_group_subject(
            group=group,
            subject=subject,
            academic_year=academic_year,
            period=period,
        )
    )
