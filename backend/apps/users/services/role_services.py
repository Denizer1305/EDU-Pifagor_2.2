from __future__ import annotations

import logging

from django.db import transaction

from apps.users.models import UserRole

logger = logging.getLogger(__name__)


@transaction.atomic
def assign_role(*, user, role):
    """Назначает роль пользователю."""
    logger.info("assign_role user_id=%s role_id=%s", user.id, role.id)
    return UserRole.objects.get_or_create(user=user, role=role)[0]


@transaction.atomic
def remove_role(*, user, role) -> None:
    """Удаляет роль у пользователя."""
    logger.info("remove_role user_id=%s role_id=%s", user.id, role.id)
    UserRole.objects.filter(user=user, role=role).delete()
