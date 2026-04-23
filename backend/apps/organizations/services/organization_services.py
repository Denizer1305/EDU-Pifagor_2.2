from __future__ import annotations

import logging

from django.db import transaction

from apps.organizations.models import Department, Organization, OrganizationType

logger = logging.getLogger(__name__)


def _clean_str(value: str | None) -> str:
    return (value or "").strip()


@transaction.atomic
def create_organization_type(
    *,
    code: str,
    name: str,
    description: str = "",
    is_active: bool = True,
) -> OrganizationType:
    logger.info("create_organization_type started code=%s", code)
    organization_type = OrganizationType(
        code=_clean_str(code),
        name=_clean_str(name),
        description=_clean_str(description),
        is_active=is_active,
    )
    organization_type.full_clean()
    organization_type.save()
    logger.info("create_organization_type completed id=%s", organization_type.id)
    return organization_type


@transaction.atomic
def update_organization_type(
    *,
    organization_type: OrganizationType,
    **validated_data,
) -> OrganizationType:
    logger.info(
        "update_organization_type started id=%s fields=%s",
        organization_type.id,
        sorted(validated_data.keys()),
    )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(organization_type, field, value)

    organization_type.full_clean()
    organization_type.save()
    logger.info("update_organization_type completed id=%s", organization_type.id)
    return organization_type


@transaction.atomic
def create_organization(
    *,
    type: OrganizationType,
    name: str,
    short_name: str = "",
    description: str = "",
    city: str = "",
    address: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    logo=None,
    is_active: bool = True,
) -> Organization:
    logger.info("create_organization started name=%s", name.strip())
    organization = Organization(
        type=type,
        name=_clean_str(name),
        short_name=_clean_str(short_name),
        description=_clean_str(description),
        city=_clean_str(city),
        address=_clean_str(address),
        phone=_clean_str(phone),
        email=_clean_str(email),
        website=_clean_str(website),
        logo=logo,
        is_active=is_active,
    )
    organization.full_clean()
    organization.save()
    logger.info("create_organization completed id=%s", organization.id)
    return organization


@transaction.atomic
def update_organization(
    *,
    organization: Organization,
    **validated_data,
) -> Organization:
    logger.info(
        "update_organization started id=%s fields=%s",
        organization.id,
        sorted(validated_data.keys()),
    )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(organization, field, value)

    organization.full_clean()
    organization.save()
    logger.info("update_organization completed id=%s", organization.id)
    return organization


@transaction.atomic
def set_teacher_registration_code(
    *,
    organization: Organization,
    raw_code: str,
    expires_at=None,
) -> Organization:
    logger.info("set_teacher_registration_code started organization_id=%s", organization.id)
    organization.set_teacher_registration_code(
        raw_code=raw_code,
        expires_at=expires_at,
    )
    organization.full_clean()
    organization.save()
    logger.info("set_teacher_registration_code completed organization_id=%s", organization.id)
    return organization


@transaction.atomic
def disable_teacher_registration_code(*, organization: Organization) -> Organization:
    logger.info("disable_teacher_registration_code started organization_id=%s", organization.id)
    organization.disable_teacher_registration_code()
    organization.full_clean()
    organization.save(update_fields=(
        "teacher_registration_code_is_active",
        "updated_at",
    ))
    logger.info("disable_teacher_registration_code completed organization_id=%s", organization.id)
    return organization


@transaction.atomic
def clear_teacher_registration_code(*, organization: Organization) -> Organization:
    logger.info("clear_teacher_registration_code started organization_id=%s", organization.id)
    organization.clear_teacher_registration_code()
    organization.full_clean()
    organization.save(update_fields=(
        "teacher_registration_code_hash",
        "teacher_registration_code_is_active",
        "teacher_registration_code_expires_at",
        "updated_at",
    ))
    logger.info("clear_teacher_registration_code completed organization_id=%s", organization.id)
    return organization


@transaction.atomic
def create_department(
    *,
    organization: Organization,
    name: str,
    short_name: str = "",
    description: str = "",
    is_active: bool = True,
) -> Department:
    logger.info(
        "create_department started organization_id=%s name=%s",
        organization.id,
        name.strip(),
    )
    department = Department(
        organization=organization,
        name=_clean_str(name),
        short_name=_clean_str(short_name),
        description=_clean_str(description),
        is_active=is_active,
    )
    department.full_clean()
    department.save()
    logger.info("create_department completed id=%s", department.id)
    return department


@transaction.atomic
def update_department(
    *,
    department: Department,
    **validated_data,
) -> Department:
    logger.info(
        "update_department started id=%s fields=%s",
        department.id,
        sorted(validated_data.keys()),
    )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(department, field, value)

    department.full_clean()
    department.save()
    logger.info("update_department completed id=%s", department.id)
    return department
