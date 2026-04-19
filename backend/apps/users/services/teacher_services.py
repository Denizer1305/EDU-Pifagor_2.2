from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def update_teacher_profile(*, teacher_profile, **validated_data):
    """Обновляет данные сущности на основе валидированных данных."""
    logger.info("update_teacher_profile started teacher_profile_id=%s fields=%s", teacher_profile.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        setattr(teacher_profile, field, value)
    teacher_profile.full_clean()
    teacher_profile.save()
    logger.info("update_teacher_profile completed teacher_profile_id=%s", teacher_profile.id)
    return teacher_profile
