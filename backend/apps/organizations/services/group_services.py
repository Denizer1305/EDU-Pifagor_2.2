from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.organizations.models import Department, Group, GroupCurator, Organization
from apps.users.constants import ROLE_TEACHER

logger = logging.getLogger(__name__)


def _user_has_teacher_role(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not hasattr(user, "user_roles"):
        return False

    return user.user_roles.filter(role__code=ROLE_TEACHER).exists()


@transaction.atomic
def create_group(
    *,
    organization: Organization,
    name: str,
    code: str,
    study_form: str = Group.StudyFormChoices.FULL_TIME,
    department: Department | None = None,
    course_number: int | None = None,
    admission_year: int | None = None,
    graduation_year: int | None = None,
    academic_year: str = "",
    status: str = Group.StatusChoices.ACTIVE,
    description: str = "",
    is_active: bool = True,
) -> Group:
    logger.info("create_group started organization_id=%s name=%s", organization.id, name.strip())
    if department and department.organization_id != organization.id:
        raise ValidationError(
            {"department": "Подразделение должно принадлежать той же организации, что и группа."}
        )

    group = Group(
        organization=organization,
        department=department,
        name=name.strip(),
        code=code.strip(),
        study_form=study_form,
        course_number=course_number,
        admission_year=admission_year,
        graduation_year=graduation_year,
        academic_year=academic_year.strip(),
        status=status,
        description=description.strip(),
        is_active=is_active,
    )
    group.full_clean()
    group.save()
    logger.info("create_group completed id=%s", group.id)
    return group


@transaction.atomic
def update_group(*, group: Group, **validated_data) -> Group:
    logger.info("update_group started id=%s fields=%s", group.id, sorted(validated_data.keys()))
    organization = validated_data.get("organization", group.organization)
    department = validated_data.get("department", group.department)

    if department and organization and department.organization_id != organization.id:
        raise ValidationError(
            {"department": "Подразделение должно принадлежать той же организации, что и группа."}
        )

    for (
        field, value,
    ) in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(group, field, value)

    group.full_clean()
    group.save()
    logger.info("update_group completed id=%s", group.id)
    return group


@transaction.atomic
def assign_group_curator(
    *,
    group: Group,
    teacher,
    is_primary: bool = True,
    starts_at=None,
    ends_at=None,
    notes: str = "",
) -> GroupCurator:
    logger.info("assign_group_curator started group_id=%s teacher_id=%s", group.id, teacher.id)
    if not _user_has_teacher_role(teacher):
        raise ValidationError({"teacher": "Куратором группы может быть только преподаватель."})

    (
        curator, created,
    ) = GroupCurator.objects.get_or_create(
        group=group,
        teacher=teacher,
        defaults={
            "is_primary": is_primary,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "notes": notes.strip(),
        },
    )

    if not created:
        curator.is_primary = is_primary
        curator.starts_at = starts_at
        curator.ends_at = ends_at
        curator.notes = notes.strip()

    if is_primary:
        GroupCurator.objects.filter(group=group, is_primary=True).exclude(pk=curator.pk).update(is_primary=False)

    curator.full_clean()
    curator.save()
    logger.info("assign_group_curator completed curator_id=%s", curator.id)
    return curator


@transaction.atomic
def remove_group_curator(*, group: Group, teacher) -> None:
    logger.info("remove_group_curator group_id=%s teacher_id=%s", group.id, teacher.id)
    GroupCurator.objects.filter(group=group, teacher=teacher).delete()
