from __future__ import annotations

from apps.organizations.models import Department, Organization, OrganizationType
from apps.organizations.tests.factories.counters import (
    department_counter,
    organization_counter,
    organization_type_counter,
)


def create_organization_type(
    *,
    code: str | None = None,
    name: str | None = None,
    description: str = "",
    is_active: bool = True,
):
    """Создаёт тестовый тип организации."""

    index = next(organization_type_counter)

    if code is None:
        code = f"organization_type_{index}"

    if name is None:
        name = f"Тип организации {index}"

    return OrganizationType.objects.create(
        code=code,
        name=name,
        description=description,
        is_active=is_active,
    )


def create_organization(
    *,
    organization_type=None,
    name: str | None = None,
    short_name: str | None = None,
    description: str = "",
    city: str = "Москва",
    address: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    is_active: bool = True,
):
    """Создаёт тестовую образовательную организацию."""

    index = next(organization_counter)

    if organization_type is None:
        organization_type = create_organization_type()

    if name is None:
        name = f"Организация {index}"

    if short_name is None:
        short_name = f"Орг{index}"

    return Organization.objects.create(
        type=organization_type,
        name=name,
        short_name=short_name,
        description=description,
        city=city,
        address=address,
        phone=phone,
        email=email,
        website=website,
        is_active=is_active,
    )


def create_department(
    *,
    organization=None,
    name: str | None = None,
    short_name: str | None = None,
    description: str = "",
    is_active: bool = True,
):
    """Создаёт тестовое подразделение организации."""

    index = next(department_counter)

    if organization is None:
        organization = create_organization()

    if name is None:
        name = f"Отделение {index}"

    if short_name is None:
        short_name = f"Отд{index}"

    return Department.objects.create(
        organization=organization,
        name=name,
        short_name=short_name,
        description=description,
        is_active=is_active,
    )
