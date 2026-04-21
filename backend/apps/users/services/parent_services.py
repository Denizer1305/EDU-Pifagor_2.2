from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    LINK_STATUS_APPROVED,
    LINK_STATUS_PENDING,
    LINK_STATUS_REJECTED,
    LINK_STATUS_REVOKED,
    ROLE_PARENT,
)
from apps.users.models import ParentStudent
from apps.users.services.role_services import assign_role_to_user
from apps.users.services.user_services import (
    activate_user_onboarding,
    reject_user_onboarding,
)
from apps.users.validators import validate_parent_student_link


def _has_field(model, field_name: str) -> bool:
    return field_name in {field.name for field in model._meta.get_fields()}


@transaction.atomic
def create_parent_student_link_request(
    *,
    parent_user,
    student_user,
    relation_type: str,
    requested_by=None,
    comment: str = "",
    is_primary: bool = False,
) -> ParentStudent:
    existing = ParentStudent.objects.filter(
        parent=parent_user,
        student=student_user,
    ).first()

    if existing and existing.status == LINK_STATUS_PENDING:
        raise ValidationError(
            {"link": _("Запрос на связь родителя и студента уже ожидает подтверждения.")}
        )

    if existing and existing.status == LINK_STATUS_APPROVED:
        raise ValidationError(
            {"link": _("Связь родителя и студента уже подтверждена.")}
        )

    link = existing or ParentStudent(
        parent=parent_user,
        student=student_user,
    )

    link.relation_type = relation_type
    link.status = LINK_STATUS_PENDING
    link.requested_by = requested_by or parent_user
    link.comment = (comment or "").strip()

    if _has_field(ParentStudent, "is_primary"):
        link.is_primary = is_primary

    link.approved_by = None
    link.approved_at = None

    validate_parent_student_link(link)
    link.full_clean()
    link.save()
    return link


@transaction.atomic
def approve_parent_student_link(*, link, reviewer, comment: str = "") -> ParentStudent:
    link.status = LINK_STATUS_APPROVED
    link.approved_by = reviewer
    link.approved_at = timezone.now()
    link.comment = (comment or "").strip()

    validate_parent_student_link(link)
    link.full_clean()
    link.save()

    assign_role_to_user(link.parent, ROLE_PARENT)
    activate_user_onboarding(
        link.parent,
        reviewer=reviewer,
        comment=comment,
    )
    return link


@transaction.atomic
def reject_parent_student_link(*, link, reviewer, comment: str) -> ParentStudent:
    if not (comment or "").strip():
        raise ValidationError(
            {"comment": _("Для отклонения связи необходимо указать комментарий.")}
        )

    link.status = LINK_STATUS_REJECTED
    link.approved_by = reviewer
    link.approved_at = timezone.now()
    link.comment = comment.strip()

    validate_parent_student_link(link)
    link.full_clean()
    link.save()

    reject_user_onboarding(
        link.parent,
        reviewer=reviewer,
        comment=comment,
    )
    return link


@transaction.atomic
def revoke_parent_student_link(*, link, reviewer=None, comment: str = "") -> ParentStudent:
    link.status = LINK_STATUS_REVOKED
    link.approved_by = reviewer
    link.approved_at = timezone.now()
    link.comment = (comment or "").strip()

    validate_parent_student_link(link)
    link.full_clean()
    link.save()
    return link
