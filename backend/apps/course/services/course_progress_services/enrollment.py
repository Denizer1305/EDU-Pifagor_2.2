from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.course.models import CourseEnrollment
from apps.course.services.course_progress_services.ensure import (
    ensure_course_progress,
)


@transaction.atomic
def start_course_enrollment(*, enrollment: CourseEnrollment) -> CourseEnrollment:
    """Переводит зачисление в состояние прохождения курса."""

    if enrollment.status == CourseEnrollment.StatusChoices.ENROLLED:
        enrollment.status = CourseEnrollment.StatusChoices.IN_PROGRESS

    if enrollment.started_at is None:
        enrollment.started_at = timezone.now()

    enrollment.last_activity_at = timezone.now()
    enrollment.full_clean()
    enrollment.save(
        update_fields=[
            "status",
            "started_at",
            "last_activity_at",
            "updated_at",
        ]
    )

    progress = ensure_course_progress(enrollment=enrollment)
    if progress.started_at is None:
        progress.started_at = enrollment.started_at
        progress.last_activity_at = enrollment.last_activity_at
        progress.full_clean()
        progress.save(
            update_fields=[
                "started_at",
                "last_activity_at",
                "updated_at",
            ]
        )

    return enrollment
