from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from apps.users.constants import ROLE_ADMIN
from apps.users.models import ParentStudent
from apps.users.services.parent_services import (
    approve_parent_student_link,
    reject_parent_student_link,
    revoke_parent_student_link,
)


def user_is_admin(user) -> bool:
    """Проверяет, является ли пользователь администратором."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.user_roles.filter(
        role__code=ROLE_ADMIN,
        is_active=True,
    ).exists()


def django_validation_error_to_drf(exc: DjangoValidationError) -> ValidationError:
    """Преобразует Django ValidationError в DRF ValidationError."""

    payload = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
    return ValidationError(payload)


def apply_parent_student_review_action(
    *,
    link: ParentStudent,
    reviewer,
    status_value: str,
    comment: str = "",
) -> ParentStudent:
    """Применяет review-действие к связи родитель-студент."""

    if status_value == ParentStudent.LinkStatusChoices.APPROVED:
        return approve_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment=comment,
        )

    if status_value == ParentStudent.LinkStatusChoices.REJECTED:
        return reject_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment=comment,
        )

    if status_value == ParentStudent.LinkStatusChoices.REVOKED:
        return revoke_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment=comment,
        )

    raise ValidationError(
        {
            "status": "Допустимы только approved, rejected или revoked."
        }
    )
