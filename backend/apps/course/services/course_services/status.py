from __future__ import annotations

from django.db import transaction

from apps.course.models import Course
from apps.course.services.course_services.validation import (
    _validate_course_can_be_published,
)


@transaction.atomic
def publish_course(*, course: Course) -> Course:
    """Публикует курс."""

    _validate_course_can_be_published(course)

    course.status = Course.StatusChoices.PUBLISHED
    course.full_clean()
    course.save(update_fields=["status", "published_at", "updated_at"])
    return course


@transaction.atomic
def archive_course(*, course: Course) -> Course:
    """Архивирует курс и делает его неактивным."""

    course.status = Course.StatusChoices.ARCHIVED
    course.is_active = False
    course.full_clean()
    course.save(update_fields=["status", "is_active", "archived_at", "updated_at"])
    return course
