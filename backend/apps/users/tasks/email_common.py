from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.users.models import User

logger = logging.getLogger(__name__)


def get_user_for_email_task(user_id: int) -> User | None:
    """Возвращает пользователя для email-задачи или None, если он не найден."""

    try:
        return User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("Email task skipped: user %s not found", user_id)
        return None


def get_user_first_name(user: User) -> str:
    """Возвращает имя пользователя из профиля."""

    profile = getattr(user, "profile", None)
    if profile:
        return getattr(profile, "first_name", "") or ""

    return ""


def send_templated_email(
    *,
    subject: str,
    to_email: str,
    html_template: str,
    txt_template: str,
    context: dict,
) -> None:
    """Формирует и отправляет письмо по HTML/TXT-шаблонам."""

    html_body = render_to_string(html_template, context)
    text_body = render_to_string(txt_template, context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
