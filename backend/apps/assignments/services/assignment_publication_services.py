from __future__ import annotations

import logging

from django.db import transaction

from apps.assignments.models import AssignmentPublication

logger = logging.getLogger(__name__)


def _ensure_publication_editable(publication: AssignmentPublication) -> None:
    if publication.status == AssignmentPublication.StatusChoices.ARCHIVED:
        raise ValueError("Нельзя изменять архивную публикацию.")


@transaction.atomic
def create_assignment_publication(
    *,
    assignment,
    published_by,
    course=None,
    lesson=None,
    title_override: str = "",
    starts_at=None,
    due_at=None,
    available_until=None,
    status: str = AssignmentPublication.StatusChoices.DRAFT,
    is_active: bool = True,
    notes: str = "",
) -> AssignmentPublication:
    publication = AssignmentPublication(
        assignment=assignment,
        course=course or assignment.course,
        lesson=lesson or assignment.lesson,
        published_by=published_by,
        title_override=title_override,
        starts_at=starts_at,
        due_at=due_at,
        available_until=available_until,
        status=status,
        is_active=is_active,
        notes=notes,
    )
    publication.full_clean()
    publication.save()

    logger.info(
        "create_assignment_publication completed publication_id=%s assignment_id=%s",
        publication.id,
        assignment.id,
    )
    return publication


@transaction.atomic
def update_assignment_publication(
    publication: AssignmentPublication,
    **fields,
) -> AssignmentPublication:
    _ensure_publication_editable(publication)

    for field_name, value in fields.items():
        setattr(publication, field_name, value)

    publication.full_clean()
    publication.save()

    logger.info("update_assignment_publication completed publication_id=%s", publication.id)
    return publication


@transaction.atomic
def publish_assignment_publication(publication: AssignmentPublication) -> AssignmentPublication:
    _ensure_publication_editable(publication)

    publication.status = AssignmentPublication.StatusChoices.PUBLISHED
    publication.is_active = True
    publication.full_clean()
    publication.save()

    logger.info("publish_assignment_publication completed publication_id=%s", publication.id)
    return publication


@transaction.atomic
def close_assignment_publication(publication: AssignmentPublication) -> AssignmentPublication:
    _ensure_publication_editable(publication)

    publication.status = AssignmentPublication.StatusChoices.CLOSED
    publication.full_clean()
    publication.save()

    logger.info("close_assignment_publication completed publication_id=%s", publication.id)
    return publication


@transaction.atomic
def archive_assignment_publication(publication: AssignmentPublication) -> AssignmentPublication:
    publication.status = AssignmentPublication.StatusChoices.ARCHIVED
    publication.is_active = False
    publication.full_clean()
    publication.save()

    logger.info("archive_assignment_publication completed publication_id=%s", publication.id)
    return publication
