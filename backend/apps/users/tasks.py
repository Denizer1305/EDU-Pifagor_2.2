from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    LINK_STATUS_PENDING,
    ONBOARDING_STATUS_ACTIVE,
    VERIFICATION_STATUS_PENDING,
)
from apps.users.models import ParentStudent, StudentProfile, TeacherProfile, User

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
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email_task(user_id: int) -> None:
    """Отправляет приветственное письмо новому пользователю."""
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
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_verify_email_task(user_id: int, verification_url: str, expires_at: str) -> None:
    """Отправляет письмо для подтверждения электронной почты."""
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
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_reset_password_email_task(user_id: int, reset_url: str, expires_at: str) -> None:
    """Отправляет письмо для восстановления пароля."""
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
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_password_changed_email_task(user_id: int) -> None:
    """Отправляет уведомление об успешной смене пароля."""
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
    """Отправляет поздравительное письмо с днем рождения."""
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


@shared_task
def log_users_onboarding_report() -> dict:
    """
    Формирует диагностический отчёт по онбордингу пользователей.
    """
    report = {
        "generated_at": timezone.now().isoformat(),
        "pending_users": User.objects.exclude(
            onboarding_status=ONBOARDING_STATUS_ACTIVE,
        ).count(),
        "pending_student_verifications": StudentProfile.objects.filter(
            verification_status=VERIFICATION_STATUS_PENDING,
        ).count(),
        "pending_teacher_verifications": TeacherProfile.objects.filter(
            verification_status=VERIFICATION_STATUS_PENDING,
        ).count(),
        "pending_parent_links": ParentStudent.objects.filter(
            status=LINK_STATUS_PENDING,
        ).count(),
    }

    logger.info("Отчёт по онбордингу пользователей: %s", report)
    return report


@shared_task
def deactivate_stale_unverified_users(days: int = 30) -> dict:
    """
    Мягко деактивирует старые неподтверждённые учётные записи.

    Условия:
    - пользователь старше N дней;
    - почта не подтверждена;
    - онбординг не завершён.
    """
    threshold = timezone.now() - timedelta(days=days)

    with transaction.atomic():
        queryset = User.objects.filter(
            is_active=True,
            is_email_verified=False,
            created_at__lt=threshold,
        ).exclude(
            onboarding_status=User.OnboardingStatusChoices.ACTIVE,
        )

        updated_count = queryset.update(
            is_active=False,
            onboarding_status=User.OnboardingStatusChoices.BLOCKED,
            reviewed_at=timezone.now(),
            review_comment=_("Учетная запись автоматически деактивирована из-за незавершённой верификации."),
        )

    result = {
        "days": days,
        "threshold": threshold.isoformat(),
        "updated_count": updated_count,
    }

    logger.warning("Деактивация старых неподтверждённых пользователей завершена: %s", result)
    return result
