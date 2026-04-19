from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def update_user(*, user, **validated_data):
    """Обновляет данные сущности на основе валидированных данных."""
    logger.info("update_user started user_id=%s fields=%s", user.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        setattr(user, field, value)
    user.full_clean()
    user.save()
    logger.info("update_user completed user_id=%s", user.id)
    return user
