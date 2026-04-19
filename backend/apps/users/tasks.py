from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.models import User

logger = logging.getLogger(__name__)


def _send_templated_email(
    *,
    subject: str,
    to_email: str,
    html_template: str,
    txt_template: str,
    context: dict,
) -> None:
    """Формирует и отправляет письмо по шаблону."""
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


@shared_task(
    autoretry_for=(
        Exception,
    ),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email_task(user_id: int) -> None:
    """Celery-задача для отправки уведомления по email."""
    try:
        user = User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_welcome_email_task: user %s not found", user_id)
        return

    context = {
        "email_title": _("Добро пожаловать в Пифагор"),
        "heading": _("Добро пожаловать в Пифагор"),
        "preheader": _("Ваш аккаунт успешно создан."),
        "footer_note": _("Вы можете войти в систему и начать работу с платформой."),
        "first_name": getattr(user.profile, "first_name", "") if hasattr(user, "profile") else "",
        "login_url": f"{settings.FRONTEND_URL}/login",
        "current_year": timezone.now().year,
    }

    _send_templated_email(
        subject=str(_("Добро пожаловать в Пифагор")),
        to_email=user.email,
        html_template="templates/auth/welcome.html",
        txt_template="templates/auth/welcome.txt",
        context=context,
    )


@shared_task(
    autoretry_for=(
        Exception,
    ),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_verify_email_task(user_id: int, verification_url: str, expires_at: str) -> None:
    """Celery-задача для отправки уведомления по email."""
    try:
        user = User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_verify_email_task: user %s not found", user_id)
        return

    context = {
        "email_title": _("Подтверждение электронной почты"),
        "heading": _("Подтвердите электронную почту"),
        "preheader": _("Завершите регистрацию в платформе."),
        "footer_note": _("Если вы не создавали аккаунт, просто проигнорируйте это письмо."),
        "first_name": getattr(user.profile, "first_name", "") if hasattr(user, "profile") else "",
        "verification_url": verification_url,
        "expires_at": expires_at,
        "current_year": timezone.now().year,
    }

    _send_templated_email(
        subject=str(_("Подтвердите электронную почту")),
        to_email=user.email,
        html_template="templates/auth/verify_email.html",
        txt_template="templates/auth/verify_email.txt",
        context=context,
    )


@shared_task(
    autoretry_for=(
        Exception,
    ),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_reset_password_email_task(user_id: int, reset_url: str, expires_at: str) -> None:
    """Celery-задача для отправки уведомления по email."""
    try:
        user = User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_reset_password_email_task: user %s not found", user_id)
        return

    context = {
        "email_title": _("Восстановление пароля"),
        "heading": _("Восстановление пароля"),
        "preheader": _("Мы получили запрос на смену пароля."),
        "footer_note": _("Если это были не вы, просто проигнорируйте письмо."),
        "first_name": getattr(user.profile, "first_name", "") if hasattr(user, "profile") else "",
        "reset_url": reset_url,
        "expires_at": expires_at,
        "current_year": timezone.now().year,
    }

    _send_templated_email(
        subject=str(_("Восстановление пароля")),
        to_email=user.email,
        html_template="templates/auth/reset_password.html",
        txt_template="templates/auth/reset_password.txt",
        context=context,
    )


@shared_task(
    autoretry_for=(
        Exception,
    ),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_password_changed_email_task(user_id: int) -> None:
    """Celery-задача для отправки уведомления по email."""
    try:
        user = User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_password_changed_email_task: user %s not found", user_id)
        return

    context = {
        "email_title": _("Пароль изменен"),
        "heading": _("Пароль успешно изменен"),
        "preheader": _("Ваш пароль в платформе был обновлен."),
        "footer_note": _("Если это действие совершали не вы, срочно восстановите доступ."),
        "first_name": getattr(user.profile, "first_name", "") if hasattr(user, "profile") else "",
        "changed_at": timezone.localtime().strftime("%d.%m.%Y %H:%M"),
        "current_year": timezone.now().year,
    }

    _send_templated_email(
        subject=str(_("Пароль успешно изменен")),
        to_email=user.email,
        html_template="templates/auth/password_changed.html",
        txt_template="templates/auth/password_changed.txt",
        context=context,
    )


@shared_task
def send_birthday_email_task(user_id: int) -> None:
    """Celery-задача для отправки уведомления по email."""
    try:
        user = User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_birthday_email_task: user %s not found", user_id)
        return

    context = {
        "email_title": _("С днем рождения!"),
        "heading": _("С днем рождения!"),
        "preheader": _("Команда Пифагора поздравляет вас."),
        "footer_note": _("Желаем вдохновения, роста и новых достижений."),
        "first_name": getattr(user.profile, "first_name", "") if hasattr(user, "profile") else "",
        "current_year": timezone.now().year,
    }

    _send_templated_email(
        subject=str(_("С днем рождения от платформы Пифагор")),
        to_email=user.email,
        html_template="templates/system/birthday.html",
        txt_template="templates/system/birthday.txt",
        context=context,
    )
