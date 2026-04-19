from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.users.models import Profile

User = get_user_model()
logger = logging.getLogger(__name__)


@transaction.atomic
def register_user(*, email: str, password: str, first_name: str, last_name: str, patronymic: str = "", phone: str = ""):
    """Функция register_user."""
    logger.info("register_user started email=%s", email.strip().lower())
    user = User.objects.create_user(
        email=email.strip().lower(),
        password=password,
    )

    Profile.objects.create(
        user=user,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        patronymic=patronymic.strip(),
        phone=phone.strip(),
    )
    logger.info("register_user completed user_id=%s", user.id)
    return user


def change_user_password(*, user, new_password: str) -> None:
    """Функция change_user_password."""
    logger.info("change_user_password started user_id=%s", user.id)
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    logger.info("change_user_password completed user_id=%s", user.id)
