from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_BLOCKED,
    ONBOARDING_STATUS_REJECTED,
)
from apps.users.validators import validate_user_onboarding_transition


def _email_verified_field_name(user) -> str | None:
    if hasattr(user, "is_email_verified"):
        return "is_email_verified"
    return None


def set_user_onboarding_status(
    user,
    status_value: str,
    comment: str = "",
    reviewed_at=None,
    reviewed_by=None,
) -> None:
    user.onboarding_status = status_value
    user.review_comment = (comment or "").strip()
    user.reviewed_at = reviewed_at or timezone.now()

    update_fields = [
        "onboarding_status",
        "review_comment",
        "reviewed_at",
        "updated_at",
    ]

    if hasattr(user, "reviewed_by"):
        user.reviewed_by = reviewed_by
        update_fields.append("reviewed_by")

    if status_value == ONBOARDING_STATUS_ACTIVE:
        user.onboarding_completed_at = timezone.now()
        update_fields.append("onboarding_completed_at")

    validate_user_onboarding_transition(user)
    user.save(update_fields=update_fields)


def mark_user_email_verified(user) -> None:
    field_name = _email_verified_field_name(user)
    if not field_name:
        return

    if not getattr(user, field_name, False):
        setattr(user, field_name, True)
        user.save(update_fields=[field_name, "updated_at"])


def activate_user_onboarding(user, reviewer=None, comment: str = "") -> None:
    set_user_onboarding_status(
        user=user,
        status_value=ONBOARDING_STATUS_ACTIVE,
        comment=comment,
        reviewed_by=reviewer,
    )


def reject_user_onboarding(user, reviewer=None, comment: str = "") -> None:
    if not (comment or "").strip():
        raise ValidationError(
            {"comment": _("Для отклонения необходимо указать комментарий.")}
        )

    set_user_onboarding_status(
        user=user,
        status_value=ONBOARDING_STATUS_REJECTED,
        comment=comment,
        reviewed_by=reviewer,
    )


def block_user(user, reviewer=None, comment: str = "") -> None:
    user.is_active = False
    user.onboarding_status = ONBOARDING_STATUS_BLOCKED
    user.review_comment = (comment or "").strip()
    user.reviewed_at = timezone.now()

    update_fields = [
        "is_active",
        "onboarding_status",
        "review_comment",
        "reviewed_at",
        "updated_at",
    ]

    if hasattr(user, "reviewed_by"):
        user.reviewed_by = reviewer
        update_fields.append("reviewed_by")

    user.save(update_fields=update_fields)


def deactivate_user(user, reviewer=None, comment: str = "") -> None:
    user.is_active = False
    update_fields = ["is_active", "updated_at"]

    if comment:
        user.review_comment = comment.strip()
        user.reviewed_at = timezone.now()
        update_fields.extend(["review_comment", "reviewed_at"])

    if hasattr(user, "reviewed_by") and reviewer is not None:
        user.reviewed_by = reviewer
        update_fields.append("reviewed_by")

    user.save(update_fields=update_fields)
