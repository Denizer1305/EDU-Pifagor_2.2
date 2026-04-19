from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def update_profile(*, profile, **validated_data):
    """Обновляет данные сущности на основе валидированных данных."""
    logger.info("update_profile started profile_id=%s fields=%s", profile.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        setattr(profile, field, value)
    profile.full_clean()
    profile.save()
    logger.info("update_profile completed profile_id=%s", profile.id)
    return profile
