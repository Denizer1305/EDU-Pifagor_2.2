from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.models import User

logger = logging.getLogger(__name__)


@shared_task(name="apps.users.tasks.deactivate_stale_unverified_users")
def deactivate_stale_unverified_users(days: int = 30) -> dict:
    """Мягко деактивирует старые неподтверждённые учётные записи.

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
            review_comment=_(
                "Учетная запись автоматически деактивирована "
                "из-за незавершённой верификации."
            ),
        )

    result = {
        "days": days,
        "threshold": threshold.isoformat(),
        "updated_count": updated_count,
    }

    logger.warning(
        "Деактивация старых неподтверждённых пользователей завершена: %s",
        result,
    )
    return result
