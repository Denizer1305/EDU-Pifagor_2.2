from __future__ import annotations

import logging

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.course.models import Course, CourseEnrollment
from apps.course.selectors import get_course_enrollments_queryset

logger = logging.getLogger(__name__)


@shared_task
def recalculate_course_structure_metrics(course_id: int) -> dict:
    course = Course.objects.filter(id=course_id).first()
    if course is None:
        return {
            "success": False,
            "message": "Курс не найден.",
            "course_id": course_id,
        }

    total_minutes = (
        course.lessons.filter(
            is_published=True,
            module__is_published=True,
        )
        .aggregate(total=Sum("estimated_minutes"))
        .get("total")
        or 0
    )

    if course.estimated_minutes != total_minutes:
        course.estimated_minutes = total_minutes
        course.save(update_fields=["estimated_minutes", "updated_at"])

    logger.info(
        "Course structure metrics recalculated course_id=%s estimated_minutes=%s",
        course.id,
        course.estimated_minutes,
    )

    return {
        "success": True,
        "course_id": course.id,
        "estimated_minutes": course.estimated_minutes,
    }


@shared_task
def recalculate_course_progress_for_enrollment(enrollment_id: int) -> dict:
    enrollment = CourseEnrollment.objects.filter(id=enrollment_id).first()
    if enrollment is None:
        return {
            "success": False,
            "message": "Запись на курс не найдена.",
            "enrollment_id": enrollment_id,
        }

    from apps.course.services.course_progress_services import (
        recalculate_course_progress,
    )

    progress = recalculate_course_progress(enrollment=enrollment)

    logger.info(
        "Course progress recalculated enrollment_id=%s progress_percent=%s",
        enrollment.id,
        progress.progress_percent,
    )

    return {
        "success": True,
        "enrollment_id": enrollment.id,
        "progress_percent": progress.progress_percent,
    }


@shared_task
def recalculate_course_progress_for_course(course_id: int) -> dict:
    enrollments = get_course_enrollments_queryset(course_id=course_id)
    processed = 0

    from apps.course.services.course_progress_services import (
        recalculate_course_progress,
    )

    for enrollment in enrollments:
        recalculate_course_progress(enrollment=enrollment)
        processed += 1

    logger.info(
        "Course progress recalculated for course_id=%s enrollments_processed=%s",
        course_id,
        processed,
    )

    return {
        "success": True,
        "course_id": course_id,
        "processed": processed,
    }


@shared_task
def archive_finished_courses() -> dict:
    now = timezone.now()
    queryset = Course.objects.filter(
        status=Course.StatusChoices.PUBLISHED,
        is_active=True,
        ends_at__isnull=False,
        ends_at__lt=now,
    )

    archived_count = 0

    for course in queryset.iterator():
        course.status = Course.StatusChoices.ARCHIVED
        course.is_active = False
        if course.archived_at is None:
            course.archived_at = now
        course.full_clean()
        course.save(update_fields=["status", "is_active", "archived_at", "updated_at"])
        archived_count += 1

    logger.info("Archived finished courses count=%s", archived_count)

    return {
        "success": True,
        "archived_count": archived_count,
    }


@shared_task
def log_courses_summary() -> dict:
    summary = {
        "total": Course.objects.count(),
        "draft": Course.objects.filter(status=Course.StatusChoices.DRAFT).count(),
        "published": Course.objects.filter(
            status=Course.StatusChoices.PUBLISHED
        ).count(),
        "archived": Course.objects.filter(status=Course.StatusChoices.ARCHIVED).count(),
        "templates": Course.objects.filter(is_template=True).count(),
        "active": Course.objects.filter(is_active=True).count(),
        "self_enrollment_enabled": Course.objects.filter(
            allow_self_enrollment=True
        ).count(),
        "generated_at": timezone.now().isoformat(),
    }

    logger.info("Courses summary: %s", summary)
    return summary
