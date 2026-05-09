from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.organizations.models import Department, Organization, OrganizationType


def _clean_str(value: str | None) -> str:
    return (value or "").strip()


def get_organization_types_queryset(
    *,
    search: str | None = None,
    is_active: bool | None = None,
):
    queryset = OrganizationType.objects.all()

    search = _clean_str(search)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(code__icontains=search)
            | Q(description__icontains=search)
        )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.order_by("name", "code")


def get_active_organization_types_queryset():
    return get_organization_types_queryset(is_active=True)


def get_organizations_queryset(
    *,
    search: str | None = None,
    organization_type_id: int | None = None,
    city: str | None = None,
    is_active: bool | None = None,
    has_active_teacher_registration_code: bool | None = None,
):
    queryset = Organization.objects.select_related("type").all()

    search = _clean_str(search)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(short_name__icontains=search)
            | Q(description__icontains=search)
            | Q(city__icontains=search)
            | Q(address__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
            | Q(website__icontains=search)
        )

    if organization_type_id is not None:
        queryset = queryset.filter(type_id=organization_type_id)

    city = _clean_str(city)
    if city:
        queryset = queryset.filter(city__icontains=city)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if has_active_teacher_registration_code is True:
        queryset = queryset.filter(
            teacher_registration_code_hash__gt="",
            teacher_registration_code_is_active=True,
        ).filter(
            Q(teacher_registration_code_expires_at__isnull=True)
            | Q(teacher_registration_code_expires_at__gt=timezone.now())
        )

    if has_active_teacher_registration_code is False:
        queryset = queryset.exclude(
            pk__in=get_organizations_queryset(
                has_active_teacher_registration_code=True
            ).values_list("pk", flat=True)
        )

    return queryset.distinct().order_by("name")


def get_active_organizations_queryset():
    return get_organizations_queryset(is_active=True)


def get_organizations_with_active_teacher_registration_code_queryset():
    return get_organizations_queryset(has_active_teacher_registration_code=True)


def get_organization_with_active_teacher_registration_code(organization_id: int):
    return (
        get_organizations_queryset(
            has_active_teacher_registration_code=True,
        )
        .filter(id=organization_id)
        .first()
    )


def get_departments_queryset(
    *,
    search: str | None = None,
    organization_id: int | None = None,
    is_active: bool | None = None,
):
    queryset = Department.objects.select_related("organization").all()

    search = _clean_str(search)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(short_name__icontains=search)
            | Q(description__icontains=search)
            | Q(organization__name__icontains=search)
            | Q(organization__short_name__icontains=search)
        )

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.distinct().order_by("organization__name", "name")


def get_active_departments_queryset():
    return get_departments_queryset(is_active=True)


def get_departments_by_organization_queryset(
    organization_id: int,
    *,
    only_active: bool = True,
):
    return get_departments_queryset(
        organization_id=organization_id,
        is_active=True if only_active else None,
    )
