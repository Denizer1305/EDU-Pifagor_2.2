from __future__ import annotations

from django.db import transaction

from apps.assignments.models import Assignment, AssignmentAttachment


@transaction.atomic
def create_assignment_attachment(
    *,
    assignment: Assignment,
    title: str,
    attachment_type: str = AssignmentAttachment.AttachmentTypeChoices.REFERENCE,
    file=None,
    external_url: str = "",
    is_visible_to_students: bool = True,
    order: int = 1,
    variant=None,
) -> AssignmentAttachment:
    """Создаёт вложение работы."""

    attachment = AssignmentAttachment(
        assignment=assignment,
        variant=variant,
        title=title,
        attachment_type=attachment_type,
        file=file,
        external_url=external_url,
        is_visible_to_students=is_visible_to_students,
        order=order,
    )
    attachment.full_clean()
    attachment.save()
    return attachment


@transaction.atomic
def update_assignment_attachment(
    attachment: AssignmentAttachment,
    **fields,
) -> AssignmentAttachment:
    """Обновляет вложение работы."""

    for field_name, value in fields.items():
        setattr(attachment, field_name, value)

    attachment.full_clean()
    attachment.save()
    return attachment


@transaction.atomic
def delete_assignment_attachment(attachment: AssignmentAttachment) -> None:
    """Удаляет вложение работы."""

    attachment.delete()
