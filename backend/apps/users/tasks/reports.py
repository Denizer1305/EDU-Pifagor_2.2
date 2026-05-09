from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.users.constants import (
    LINK_STATUS_PENDING,
    ONBOARDING_STATUS_ACTIVE,
    VERIFICATION_STATUS_PENDING,
)
from apps.users.models import ParentStudent, StudentProfile, TeacherProfile, User

logger = logging.getLogger(__name__)


@shared_task(name="apps.users.tasks.log_users_onboarding_report")
def log_users_onboarding_report() -> dict:
    """Формирует диагностический отчёт по онбордингу пользователей."""

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
