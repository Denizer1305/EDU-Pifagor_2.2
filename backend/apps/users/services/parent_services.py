from __future__ import annotations

import logging

from apps.users.models import ParentStudent

logger = logging.getLogger(__name__)


def update_parent_profile(*, parent_profile, **validated_data):
    """Обновляет данные сущности на основе валидированных данных."""
    logger.info("update_parent_profile started parent_profile_id=%s fields=%s", parent_profile.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        setattr(parent_profile, field, value)
    parent_profile.full_clean()
    parent_profile.save()
    logger.info("update_parent_profile completed parent_profile_id=%s", parent_profile.id)
    return parent_profile


def create_parent_student_link(*, parent, student, relation_type: str, is_primary: bool = False):
    """Создает и возвращает новую сущность."""
    logger.info("create_parent_student_link started parent_id=%s student_id=%s", parent.id, student.id)
    (
        link, _,
    ) = ParentStudent.objects.get_or_create(
        parent=parent,
        student=student,
        defaults={
            "relation_type": relation_type,
            "is_primary": is_primary,
        },
    )
    logger.info("create_parent_student_link completed link_id=%s", link.id)
    return link
