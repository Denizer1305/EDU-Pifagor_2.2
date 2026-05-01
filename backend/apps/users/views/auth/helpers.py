from __future__ import annotations

import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.users.serializers.auth import (
    ParentRegistrationSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def get_frontend_url(path: str, token: str) -> str:
    """Формирует frontend-ссылку с token query-параметром."""

    base_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{base_url}{path}?{urlencode({'token': token})}"


def safe_delay(task, *args) -> None:
    """Безопасно ставит Celery-задачу в очередь."""

    try:
        task.delay(*args)
    except Exception:  # pragma: no cover
        logger.exception(
            "Не удалось поставить Celery-задачу %s в очередь.",
            getattr(task, "__name__", task),
        )


def get_register_serializer_class(registration_type: str):
    """Возвращает serializer регистрации по типу пользователя."""

    registration_type = (registration_type or "").strip().lower()

    mapping = {
        User.RegistrationTypeChoices.STUDENT: StudentRegistrationSerializer,
        User.RegistrationTypeChoices.PARENT: ParentRegistrationSerializer,
        User.RegistrationTypeChoices.TEACHER: TeacherRegistrationSerializer,
    }

    serializer_class = mapping.get(registration_type)

    if serializer_class is None:
        raise ValidationError(
            {
                "registration_type": _(
                    "Допустимые значения: student, parent, teacher."
                )
            }
        )

    return serializer_class
