from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def update_student_profile(*, student_profile, **validated_data):
    """Обновляет данные сущности на основе валидированных данных."""
    logger.info("update_student_profile started student_profile_id=%s fields=%s", student_profile.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        setattr(student_profile, field, value)
    student_profile.full_clean()
    student_profile.save()
    logger.info("update_student_profile completed student_profile_id=%s", student_profile.id)
    return student_profile
