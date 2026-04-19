from __future__ import annotations

from apps.organizations.models import Department, Organization, OrganizationType


def get_organization_types_queryset():
    return OrganizationType.objects.all()


def get_active_organization_types_queryset():
    return OrganizationType.objects.filter(is_active=True)


def get_organizations_queryset():
    return Organization.objects.select_related("type").all()


def get_active_organizations_queryset():
    return Organization.objects.select_related("type").filter(is_active=True)


def get_departments_queryset():
    return Department.objects.select_related("organization").all()


def get_active_departments_queryset():
    return Department.objects.select_related("organization").filter(is_active=True)
