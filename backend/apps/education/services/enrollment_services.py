from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.education.models import AcademicYear, StudentGroupEnrollment
from apps.organizations.models import Group


def _normalize_str(value):
    return value.strip() if isinstance(value, str) else value


def _get_user_role_codes(user) -> set[str]:
    if not user:
        return set()

    if getattr(user, "is_superuser", False):
        return {"admin"}

    if not hasattr(user, "user_roles"):
        return set()

    return set(user.user_roles.values_list("role__code", flat=True))


def _user_has_student_role(user) -> bool:
    role_codes = _get_user_role_codes(user)
    return "student" in role_codes or getattr(user, "is_superuser", False)


@transaction.atomic
def create_student_group_enrollment(
    *,
    student,
    group: Group,
    academic_year: AcademicYear,
    enrollment_date,
    completion_date=None,
    status: str = StudentGroupEnrollment.StatusChoices.ACTIVE,
    is_primary: bool = True,
    journal_number: int | None = None,
    notes: str = "",
) -> StudentGroupEnrollment:
    if not _user_has_student_role(student):
        raise ValidationError(
            {"student": "Зачисление в группу можно создать только для студента."}
        )

    if is_primary:
        StudentGroupEnrollment.objects.filter(
            student=student,
            academic_year=academic_year,
            is_primary=True,
        ).update(is_primary=False)

    enrollment = StudentGroupEnrollment(
        student=student,
        group=group,
        academic_year=academic_year,
        enrollment_date=enrollment_date,
        completion_date=completion_date,
        status=status,
        is_primary=is_primary,
        journal_number=journal_number,
        notes=_normalize_str(notes),
    )
    enrollment.full_clean()
    enrollment.save()
    return enrollment


@transaction.atomic
def update_student_group_enrollment(
    *,
    enrollment: StudentGroupEnrollment,
    **validated_data,
) -> StudentGroupEnrollment:
    student = validated_data.get("student", enrollment.student)
    academic_year = validated_data.get("academic_year", enrollment.academic_year)
    is_primary = validated_data.get("is_primary", enrollment.is_primary)

    if not _user_has_student_role(student):
        raise ValidationError(
            {"student": "Зачисление в группу можно сохранить только для студента."}
        )

    if is_primary:
        StudentGroupEnrollment.objects.exclude(pk=enrollment.pk).filter(
            student=student,
            academic_year=academic_year,
            is_primary=True,
        ).update(is_primary=False)

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = _normalize_str(value)
        setattr(enrollment, field, value)

    enrollment.full_clean()
    enrollment.save()
    return enrollment
