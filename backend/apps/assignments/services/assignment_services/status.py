from __future__ import annotations

import logging

from django.db import transaction

from apps.assignments.models import Assignment

logger = logging.getLogger(__name__)


@transaction.atomic
def publish_assignment(assignment: Assignment) -> Assignment:
    """Переводит работу в статус опубликованной."""

    logger.info("publish_assignment started assignment_id=%s", assignment.id)

    assignment.status = Assignment.StatusChoices.PUBLISHED
    assignment.is_active = True
    assignment.full_clean()
    assignment.save()

    logger.info("publish_assignment completed assignment_id=%s", assignment.id)
    return assignment


@transaction.atomic
def archive_assignment(assignment: Assignment) -> Assignment:
    """Архивирует работу и отключает её активность."""

    logger.info("archive_assignment started assignment_id=%s", assignment.id)

    assignment.status = Assignment.StatusChoices.ARCHIVED
    assignment.is_active = False
    assignment.full_clean()
    assignment.save()

    logger.info("archive_assignment completed assignment_id=%s", assignment.id)
    return assignment
