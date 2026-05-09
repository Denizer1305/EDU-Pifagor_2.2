from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.tasks.email_common import (
    get_user_first_name,
    get_user_for_email_task,
    send_templated_email,
)


@shared_task(
    name="apps.users.tasks.send_welcome_email_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email_task(user_id: int) -> None:
    """Отправляет приветственное письмо новому пользователю."""

    user = get_user_for_email_task(user_id)
    if user is None:
        return

    context = {
        "email_title": _("Добро пожаловать в Пифагор"),
        "heading": _("Добро пожаловать в Пифагор"),
        "preheader": _("Ваш аккаунт успешно создан."),
        "footer_note": _("Вы можете войти в систему и начать работу с платформой."),
        "first_name": get_user_first_name(user),
        "login_url": f"{settings.FRONTEND_URL}/login",
        "current_year": timezone.now().year,
    }

    send_templated_email(
        subject=str(_("Добро пожаловать в Пифагор")),
        to_email=user.email,
        html_template="templates/auth/welcome.html",
        txt_template="templates/auth/welcome.txt",
        context=context,
    )


@shared_task(
    name="apps.users.tasks.send_verify_email_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_verify_email_task(
    user_id: int,
    verification_url: str,
    expires_at: str,
) -> None:
    """Отправляет письмо для подтверждения электронной почты."""

    user = get_user_for_email_task(user_id)
    if user is None:
        return

    context = {
        "email_title": _("Подтверждение электронной почты"),
        "heading": _("Подтвердите электронную почту"),
        "preheader": _("Завершите регистрацию в платформе."),
        "footer_note": _(
            "Если вы не создавали аккаунт, просто проигнорируйте это письмо."
        ),
        "first_name": get_user_first_name(user),
        "verification_url": verification_url,
        "expires_at": expires_at,
        "current_year": timezone.now().year,
    }

    send_templated_email(
        subject=str(_("Подтвердите электронную почту")),
        to_email=user.email,
        html_template="templates/auth/verify_email.html",
        txt_template="templates/auth/verify_email.txt",
        context=context,
    )


@shared_task(
    name="apps.users.tasks.send_reset_password_email_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_reset_password_email_task(
    user_id: int,
    reset_url: str,
    expires_at: str,
) -> None:
    """Отправляет письмо для восстановления пароля."""

    user = get_user_for_email_task(user_id)
    if user is None:
        return

    context = {
        "email_title": _("Восстановление пароля"),
        "heading": _("Восстановление пароля"),
        "preheader": _("Мы получили запрос на смену пароля."),
        "footer_note": _("Если это были не вы, просто проигнорируйте письмо."),
        "first_name": get_user_first_name(user),
        "reset_url": reset_url,
        "expires_at": expires_at,
        "current_year": timezone.now().year,
    }

    send_templated_email(
        subject=str(_("Восстановление пароля")),
        to_email=user.email,
        html_template="templates/auth/reset_password.html",
        txt_template="templates/auth/reset_password.txt",
        context=context,
    )


@shared_task(
    name="apps.users.tasks.send_password_changed_email_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_password_changed_email_task(user_id: int) -> None:
    """Отправляет уведомление об успешной смене пароля."""

    user = get_user_for_email_task(user_id)
    if user is None:
        return

    context = {
        "email_title": _("Пароль изменен"),
        "heading": _("Пароль успешно изменен"),
        "preheader": _("Ваш пароль в платформе был обновлен."),
        "footer_note": _(
            "Если это действие совершали не вы, срочно восстановите доступ."
        ),
        "first_name": get_user_first_name(user),
        "changed_at": timezone.localtime().strftime("%d.%m.%Y %H:%M"),
        "current_year": timezone.now().year,
    }

    send_templated_email(
        subject=str(_("Пароль успешно изменен")),
        to_email=user.email,
        html_template="templates/auth/password_changed.html",
        txt_template="templates/auth/password_changed.txt",
        context=context,
    )
