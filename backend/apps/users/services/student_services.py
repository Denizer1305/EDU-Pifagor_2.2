from __future__ import annotations

import logging

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    ONBOARDING_STATUS_PENDING,
    ROLE_STUDENT,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
)
from apps.users.services.role_services import assign_role_to_user
from apps.users.services.user_services import (
    activate_user_onboarding,
    reject_user_onboarding,
)
from apps.users.validators import validate_student_profile_request

logger = logging.getLogger(__name__)


def _verify_group_join_code(group, code: str) -> None:
    """
    Проверяет код группы.

    Работает мягко:
    если поля кодов ещё не добавлены в Group, flow не ломается.
    """
    code = (code or "").strip()
    if not code:
        raise ValidationError({"submitted_group_code": _("Необходимо указать код группы.")})

    has_hash = hasattr(group, "join_code_hash")
    has_active = hasattr(group, "join_code_is_active")
    has_expires = hasattr(group, "join_code_expires_at")

    if not has_hash:
        return

    code_hash = getattr(group, "join_code_hash", "") or ""
    if not code_hash:
        raise ValidationError({"submitted_group_code": _("Для группы не настроен код присоединения.")})

    if has_active and not getattr(group, "join_code_is_active", False):
        raise ValidationError({"submitted_group_code": _("Код группы отключён.")})

    if has_expires:
        expires_at = getattr(group, "join_code_expires_at", None)
        if expires_at and timezone.now() > expires_at:
            raise ValidationError({"submitted_group_code": _("Срок действия кода группы истёк.")})

    if not check_password(code, code_hash):
        raise ValidationError({"submitted_group_code": _("Неверный код группы.")})


def _try_sync_student_group_enrollment(
    *,
    student_profile,
    reviewer=None,
    academic_year=None,
    enrollment_date=None,
) -> None:
    """
    Пытается синхронизировать StudentGroupEnrollment.

    Если education ещё не готово или структура отличается,
    users-flow не ломается.
    """
    try:
        from apps.education.models import AcademicYear, StudentGroupEnrollment
    except Exception:  # pragma: no cover
        return

    if not student_profile.requested_group:
        return

    if academic_year is None:
        academic_year = (
            AcademicYear.objects.filter(is_current=True, is_active=True).first()
            or AcademicYear.objects.filter(is_active=True).order_by("-start_date").first()
        )

    if academic_year is None:
        return

    try:
        enrollment, created = StudentGroupEnrollment.objects.get_or_create(
            student=student_profile.user,
            group=student_profile.requested_group,
            academic_year=academic_year,
            defaults={
                "enrollment_date": enrollment_date or timezone.localdate(),
                "status": StudentGroupEnrollment.StatusChoices.ACTIVE,
                "is_primary": True,
            },
        )

        if not created:
            changed = False

            if hasattr(enrollment, "status") and enrollment.status != StudentGroupEnrollment.StatusChoices.ACTIVE:
                enrollment.status = StudentGroupEnrollment.StatusChoices.ACTIVE
                changed = True

            if hasattr(enrollment, "is_primary") and not enrollment.is_primary:
                enrollment.is_primary = True
                changed = True

            if changed:
                enrollment.full_clean()
                enrollment.save()
    except Exception:  # pragma: no cover
        logger.exception(
            "Не удалось синхронизировать StudentGroupEnrollment для user_id=%s",
            student_profile.user_id,
        )


@transaction.atomic
def submit_student_group_request(
    *,
    student_profile,
    requested_organization,
    requested_department=None,
    requested_group,
    submitted_group_code: str,
    admission_year: int | None = None,
    graduation_year: int | None = None,
    student_code: str = "",
    notes: str = "",
):
    """
    Сохраняет заявку студента на учебную привязку.
    """
    if requested_department and requested_department.organization_id != requested_organization.id:
        raise ValidationError(
            {"requested_department": _("Отделение должно принадлежать выбранной образовательной организации.")}
        )

    if requested_group.organization_id != requested_organization.id:
        raise ValidationError(
            {"requested_group": _("Группа должна принадлежать выбранной образовательной организации.")}
        )

    if requested_department and requested_group.department_id and requested_group.department_id != requested_department.id:
        raise ValidationError(
            {"requested_group": _("Группа должна принадлежать выбранному отделению.")}
        )

    _verify_group_join_code(requested_group, submitted_group_code)

    student_profile.requested_organization = requested_organization
    student_profile.requested_department = requested_department
    student_profile.requested_group = requested_group
    student_profile.submitted_group_code = (submitted_group_code or "").strip()

    if hasattr(student_profile, "student_code"):
        student_profile.student_code = (student_code or "").strip()
    if hasattr(student_profile, "notes"):
        student_profile.notes = (notes or "").strip()
    if hasattr(student_profile, "admission_year") and admission_year is not None:
        student_profile.admission_year = admission_year
    if hasattr(student_profile, "graduation_year") and graduation_year is not None:
        student_profile.graduation_year = graduation_year

    student_profile.verification_status = VERIFICATION_STATUS_PENDING
    student_profile.verified_by = None
    student_profile.verified_at = None
    student_profile.verification_comment = ""

    validate_student_profile_request(student_profile)
    student_profile.full_clean()
    student_profile.save()

    user = student_profile.user
    if user.is_email_verified:
        user.onboarding_status = ONBOARDING_STATUS_PENDING
        user.save(update_fields=["onboarding_status", "updated_at"])

    return student_profile


@transaction.atomic
def approve_student_profile(
    *,
    student_profile,
    reviewer,
    comment: str = "",
    academic_year=None,
    enrollment_date=None,
):
    """
    Подтверждает учебную привязку студента.
    """
    student_profile.verification_status = VERIFICATION_STATUS_APPROVED
    student_profile.verified_by = reviewer
    student_profile.verified_at = timezone.now()
    student_profile.verification_comment = (comment or "").strip()
    student_profile.full_clean()
    student_profile.save()

    assign_role_to_user(student_profile.user, ROLE_STUDENT)
    activate_user_onboarding(
        student_profile.user,
        reviewer=reviewer,
        comment=comment,
    )

    _try_sync_student_group_enrollment(
        student_profile=student_profile,
        reviewer=reviewer,
        academic_year=academic_year,
        enrollment_date=enrollment_date,
    )

    return student_profile


@transaction.atomic
def reject_student_profile(*, student_profile, reviewer, comment: str):
    """
    Отклоняет учебную привязку студента.
    """
    if not (comment or "").strip():
        raise ValidationError(
            {"comment": _("Для отклонения учебной привязки необходимо указать комментарий.")}
        )

    student_profile.verification_status = VERIFICATION_STATUS_REJECTED
    student_profile.verified_by = reviewer
    student_profile.verified_at = timezone.now()
    student_profile.verification_comment = comment.strip()
    student_profile.full_clean()
    student_profile.save()

    reject_user_onboarding(
        student_profile.user,
        reviewer=reviewer,
        comment=comment,
    )
    return student_profile
