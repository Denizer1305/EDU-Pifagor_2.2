from __future__ import annotations

from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.organizations.models import (
    Department,
    Group,
    GroupCurator,
    Organization,
    OrganizationType,
    Subject,
    SubjectCategory,
    TeacherOrganization,
)


def _strip_or_empty(value):
    return value.strip() if isinstance(value, str) else value


@receiver(pre_save, sender=OrganizationType)
def normalize_organization_type_fields(sender, instance, **kwargs):
    instance.code = _strip_or_empty(instance.code)
    instance.name = _strip_or_empty(instance.name)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=Organization)
def normalize_organization_fields(sender, instance, **kwargs):
    instance.name = _strip_or_empty(instance.name)
    instance.short_name = _strip_or_empty(instance.short_name)
    instance.description = _strip_or_empty(instance.description)
    instance.city = _strip_or_empty(instance.city)
    instance.address = _strip_or_empty(instance.address)
    instance.phone = _strip_or_empty(instance.phone)
    instance.email = _strip_or_empty(instance.email)
    instance.website = _strip_or_empty(instance.website)


@receiver(pre_save, sender=Department)
def normalize_department_fields(sender, instance, **kwargs):
    instance.name = _strip_or_empty(instance.name)
    instance.short_name = _strip_or_empty(instance.short_name)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=SubjectCategory)
def normalize_subject_category_fields(sender, instance, **kwargs):
    instance.code = _strip_or_empty(instance.code)
    instance.name = _strip_or_empty(instance.name)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=Subject)
def normalize_subject_fields(sender, instance, **kwargs):
    instance.name = _strip_or_empty(instance.name)
    instance.short_name = _strip_or_empty(instance.short_name)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=Group)
def normalize_group_fields(sender, instance, **kwargs):
    instance.name = _strip_or_empty(instance.name)
    instance.code = _strip_or_empty(instance.code)
    instance.academic_year = _strip_or_empty(instance.academic_year)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=GroupCurator)
def normalize_group_curator_fields(sender, instance, **kwargs):
    instance.notes = _strip_or_empty(instance.notes)


@receiver(pre_save, sender=TeacherOrganization)
def normalize_teacher_organization_fields(sender, instance, **kwargs):
    instance.position = _strip_or_empty(instance.position)
    instance.notes = _strip_or_empty(instance.notes)
