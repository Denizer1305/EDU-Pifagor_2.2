from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.assignments.models import (
    Submission,
    SubmissionAttachment,
)


@transaction.atomic
def attach_file_to_submission(
    *,
    submission: Submission,
    file,
    question=None,
    attachment_type: str = SubmissionAttachment.AttachmentTypeChoices.OTHER,
) -> SubmissionAttachment:
    """Прикрепляет файл к сдаче студента."""

    if submission.status not in {
        Submission.StatusChoices.DRAFT,
        Submission.StatusChoices.IN_PROGRESS,
        Submission.StatusChoices.RETURNED_FOR_REVISION,
    }:
        raise ValidationError("Нельзя прикреплять файлы после отправки работы.")

    attachment = SubmissionAttachment(
        submission=submission,
        question=question,
        file=file,
        attachment_type=attachment_type,
    )
    attachment.full_clean()
    attachment.save()

    return attachment
