from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.organizations.models import Subject, TeacherSubject
from apps.organizations.services.teacher_services.common import (
    _user_has_teacher_role,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def assign_teacher_subject(
    *,
    teacher,
    subject: Subject,
    is_primary: bool = False,
    is_active: bool = True,
) -> TeacherSubject:
    """Создаёт или обновляет связь преподавателя с предметом."""

    logger.info(
        "assign_teacher_subject started teacher_id=%s subject_id=%s",
        teacher.id,
        subject.id,
    )

    if not _user_has_teacher_role(teacher):
        raise ValidationError(
            {
                "teacher": (
                    "Связь с предметом можно создать только для преподавателя."
                )
            }
        )

    link, created = TeacherSubject.objects.get_or_create(
        teacher=teacher,
        subject=subject,
        defaults={
            "is_primary": is_primary,
            "is_active": is_active,
        },
    )

    if not created:
        link.is_primary = is_primary
        link.is_active = is_active

    if is_primary and is_active:
        TeacherSubject.objects.filter(
            teacher=teacher,
            is_primary=True,
            is_active=True,
        ).exclude(pk=link.pk).update(is_primary=False)

    link.full_clean()
    link.save()

    logger.info("assign_teacher_subject completed link_id=%s", link.id)
    return link


@transaction.atomic
def remove_teacher_subject(
    *,
    teacher,
    subject: Subject,
) -> None:
    """Деактивирует связь преподавателя с предметом."""

    logger.info(
        "remove_teacher_subject started teacher_id=%s subject_id=%s",
        teacher.id,
        subject.id,
    )

    link = TeacherSubject.objects.filter(
        teacher=teacher,
        subject=subject,
    ).first()

    if not link:
        logger.info(
            "remove_teacher_subject skipped teacher_id=%s subject_id=%s not_found",
            teacher.id,
            subject.id,
        )
        return

    link.is_active = False
    link.is_primary = False
    link.full_clean()
    link.save(
        update_fields=(
            "is_active",
            "is_primary",
            "updated_at",
        )
    )

    logger.info("remove_teacher_subject completed link_id=%s", link.id)
