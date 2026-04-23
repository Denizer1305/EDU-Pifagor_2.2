from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    ROLE_TEACHER,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
)
from apps.users.services.role_services import assign_role_to_user
from apps.users.services.user_services import (
    activate_user_onboarding,
    reject_user_onboarding,
)
from apps.users.validators import validate_teacher_profile_request

logger = logging.getLogger(__name__)


def _has_field(model, field_name: str) -> bool:
    return field_name in {field.name for field in model._meta.get_fields()}


def _try_sync_teacher_organization_link(teacher_profile) -> None:
    try:
        from apps.organizations.models import TeacherOrganization
    except Exception:
        return

    organization = teacher_profile.requested_organization
    if not organization:
        return

    try:
        defaults = {}
        teacher_org_fields = {field.name for field in TeacherOrganization._meta.get_fields()}

        if "is_active" in teacher_org_fields:
            defaults["is_active"] = True
        if "is_primary" in teacher_org_fields:
            defaults["is_primary"] = True

        TeacherOrganization.objects.get_or_create(
            teacher=teacher_profile.user,
            organization=organization,
            defaults=defaults,
        )
    except Exception:
        logger.exception(
            "Не удалось синхронизировать TeacherOrganization для user_id=%s",
            teacher_profile.user_id,
        )


@transaction.atomic
def submit_teacher_verification_request(
    *,
    teacher_profile,
    requested_organization,
    requested_department=None,
    position: str = "",
    employee_code: str = "",
    education_info: str = "",
    experience_years: int | None = None,
    public_title: str | None = None,
    short_bio: str | None = None,
    bio: str | None = None,
    education: str | None = None,
    experience: int | None = None,
    achievements: str | None = None,
    is_public=None,
    show_on_teachers_page=None,
):
    if requested_department and requested_department.organization_id != requested_organization.id:
        raise ValidationError(
            {"requested_department": _("Отделение должно принадлежать выбранной образовательной организации.")}
        )

    teacher_profile.requested_organization = requested_organization
    teacher_profile.requested_department = requested_department

    # Новая схема
    if _has_field(teacher_profile.__class__, "position"):
        teacher_profile.position = (position or "").strip()

    if _has_field(teacher_profile.__class__, "employee_code"):
        teacher_profile.employee_code = (employee_code or "").strip()

    if _has_field(teacher_profile.__class__, "education_info"):
        teacher_profile.education_info = (education_info or "").strip()

    if _has_field(teacher_profile.__class__, "experience_years") and experience_years is not None:
        teacher_profile.experience_years = experience_years

    # Старая схема — обновляем только если значение реально передано
    if _has_field(teacher_profile.__class__, "public_title") and public_title is not None:
        teacher_profile.public_title = public_title.strip()

    if _has_field(teacher_profile.__class__, "short_bio") and short_bio is not None:
        teacher_profile.short_bio = short_bio.strip()

    if _has_field(teacher_profile.__class__, "bio") and bio is not None:
        teacher_profile.bio = bio.strip()

    if _has_field(teacher_profile.__class__, "education") and education is not None:
        teacher_profile.education = education.strip()

    if _has_field(teacher_profile.__class__, "experience") and experience is not None:
        teacher_profile.experience = experience

    if _has_field(teacher_profile.__class__, "achievements") and achievements is not None:
        teacher_profile.achievements = achievements.strip()

    if _has_field(teacher_profile.__class__, "is_public") and is_public is not None:
        teacher_profile.is_public = is_public

    if _has_field(teacher_profile.__class__, "show_on_teachers_page") and show_on_teachers_page is not None:
        teacher_profile.show_on_teachers_page = show_on_teachers_page

    teacher_profile.verification_status = VERIFICATION_STATUS_PENDING
    teacher_profile.verified_by = None
    teacher_profile.verified_at = None
    teacher_profile.verification_comment = ""

    if _has_field(teacher_profile.__class__, "code_verified_at"):
        teacher_profile.code_verified_at = timezone.now()

    validate_teacher_profile_request(teacher_profile)
    teacher_profile.full_clean()
    teacher_profile.save()

    return teacher_profile


@transaction.atomic
def approve_teacher_profile(*, teacher_profile, reviewer, comment: str = ""):
    teacher_profile.verification_status = VERIFICATION_STATUS_APPROVED
    teacher_profile.verified_by = reviewer
    teacher_profile.verified_at = timezone.now()
    teacher_profile.verification_comment = (comment or "").strip()
    teacher_profile.full_clean()
    teacher_profile.save()

    assign_role_to_user(teacher_profile.user, ROLE_TEACHER)
    activate_user_onboarding(
        teacher_profile.user,
        reviewer=reviewer,
        comment=comment,
    )
    _try_sync_teacher_organization_link(teacher_profile)

    return teacher_profile


@transaction.atomic
def reject_teacher_profile(*, teacher_profile, reviewer, comment: str):
    if not (comment or "").strip():
        raise ValidationError(
            {"comment": _("Для отклонения преподавательского профиля необходимо указать комментарий.")}
        )

    teacher_profile.verification_status = VERIFICATION_STATUS_REJECTED
    teacher_profile.verified_by = reviewer
    teacher_profile.verified_at = timezone.now()
    teacher_profile.verification_comment = comment.strip()
    teacher_profile.full_clean()
    teacher_profile.save()

    reject_user_onboarding(
        teacher_profile.user,
        reviewer=reviewer,
        comment=comment,
    )
    return teacher_profile
