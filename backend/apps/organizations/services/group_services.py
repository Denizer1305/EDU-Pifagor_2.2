from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.organizations.models import Department, Group, GroupCurator, Organization
from apps.users.constants import ROLE_TEACHER

logger = logging.getLogger(__name__)


def _clean_str(value: str | None) -> str:
    return (value or "").strip()


def _has_teacher_role(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if getattr(user, "registration_type", "") == "teacher":
        return True

    if not hasattr(user, "user_roles"):
        return False

    queryset = user.user_roles.filter(role__code=ROLE_TEACHER)
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return queryset.exists()


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
    logger.info(
        "create_group started organization_id=%s name=%s", organization.id, name.strip()
    )

    if department and department.organization_id != organization.id:
        raise ValidationError(
            {
                "department": "Подразделение должно принадлежать той же организации, что и группа."
            }
        )

    group = Group(
        organization=organization,
        department=department,
        name=_clean_str(name),
        code=_clean_str(code),
        study_form=study_form,
        course_number=course_number,
        admission_year=admission_year,
        graduation_year=graduation_year,
        academic_year=_clean_str(academic_year),
        status=status,
        description=_clean_str(description),
        is_active=is_active,
    )
    group.full_clean()
    group.save()
    logger.info("create_group completed id=%s", group.id)
    return group


@transaction.atomic
def update_group(*, group: Group, **validated_data) -> Group:
    logger.info(
        "update_group started id=%s fields=%s", group.id, sorted(validated_data.keys())
    )

    organization = validated_data.get("organization", group.organization)
    department = validated_data.get("department", group.department)

    if department and organization and department.organization_id != organization.id:
        raise ValidationError(
            {
                "department": "Подразделение должно принадлежать той же организации, что и группа."
            }
        )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(group, field, value)

    group.full_clean()
    group.save()
    logger.info("update_group completed id=%s", group.id)
    return group


@transaction.atomic
def set_group_join_code(
    *,
    group: Group,
    raw_code: str,
    expires_at=None,
) -> Group:
    logger.info("set_group_join_code started group_id=%s", group.id)
    group.set_join_code(
        raw_code=raw_code,
        expires_at=expires_at,
    )
    group.full_clean()
    group.save()
    logger.info("set_group_join_code completed group_id=%s", group.id)
    return group


@transaction.atomic
def disable_group_join_code(*, group: Group) -> Group:
    logger.info("disable_group_join_code started group_id=%s", group.id)
    group.disable_join_code()
    group.full_clean()
    group.save(
        update_fields=(
            "join_code_is_active",
            "updated_at",
        )
    )
    logger.info("disable_group_join_code completed group_id=%s", group.id)
    return group


@transaction.atomic
def clear_group_join_code(*, group: Group) -> Group:
    logger.info("clear_group_join_code started group_id=%s", group.id)
    group.clear_join_code()
    group.full_clean()
    group.save(
        update_fields=(
            "join_code_hash",
            "join_code_is_active",
            "join_code_expires_at",
            "updated_at",
        )
    )
    logger.info("clear_group_join_code completed group_id=%s", group.id)
    return group


@transaction.atomic
def assign_group_curator(
    *,
    group: Group,
    teacher,
    is_primary: bool = True,
    is_active: bool = True,
    starts_at=None,
    ends_at=None,
    notes: str = "",
) -> GroupCurator:
    logger.info(
        "assign_group_curator started group_id=%s teacher_id=%s", group.id, teacher.id
    )

    if not _has_teacher_role(teacher):
        raise ValidationError(
            {"teacher": "Куратором группы может быть только преподаватель."}
        )

    curator, created = GroupCurator.objects.get_or_create(
        group=group,
        teacher=teacher,
        defaults={
            "is_primary": is_primary,
            "is_active": is_active,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "notes": _clean_str(notes),
        },
    )

    if not created:
        curator.is_primary = is_primary
        curator.is_active = is_active
        curator.starts_at = starts_at
        curator.ends_at = ends_at
        curator.notes = _clean_str(notes)

    if is_primary and is_active:
        GroupCurator.objects.filter(
            group=group,
            is_primary=True,
            is_active=True,
        ).exclude(pk=curator.pk).update(is_primary=False)

    curator.full_clean()
    curator.save()
    logger.info("assign_group_curator completed curator_id=%s", curator.id)
    return curator


@transaction.atomic
def remove_group_curator(
    *,
    group: Group,
    teacher,
) -> None:
    logger.info(
        "remove_group_curator started group_id=%s teacher_id=%s", group.id, teacher.id
    )

    curator = GroupCurator.objects.filter(
        group=group,
        teacher=teacher,
    ).first()

    if not curator:
        logger.info(
            "remove_group_curator skipped group_id=%s teacher_id=%s not_found",
            group.id,
            teacher.id,
        )
        return

    curator.is_active = False
    curator.is_primary = False
    curator.full_clean()
    curator.save(
        update_fields=(
            "is_active",
            "is_primary",
            "updated_at",
        )
    )

    logger.info("remove_group_curator completed curator_id=%s", curator.id)
