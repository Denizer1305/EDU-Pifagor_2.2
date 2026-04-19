from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.education.models import AcademicYear, EducationPeriod, GroupSubject, TeacherGroupSubject
from apps.organizations.models import Group, Subject, TeacherOrganization, TeacherSubject


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


def _user_has_teacher_role(user) -> bool:
    role_codes = _get_user_role_codes(user)
    return "teacher" in role_codes or getattr(user, "is_superuser", False)


@transaction.atomic
def create_group_subject(
    *,
    group: Group,
    subject: Subject,
    academic_year: AcademicYear,
    period: EducationPeriod,
    planned_hours: int = 0,
    contact_hours: int = 0,
    independent_hours: int = 0,
    assessment_type: str = GroupSubject.AssessmentTypeChoices.NONE,
    is_required: bool = True,
    is_active: bool = True,
    notes: str = "",
) -> GroupSubject:
    if period.academic_year_id != academic_year.id:
        raise ValidationError(
            {"period": "Учебный период должен принадлежать тому же учебному году."}
        )

    group_subject = GroupSubject(
        group=group,
        subject=subject,
        academic_year=academic_year,
        period=period,
        planned_hours=planned_hours,
        contact_hours=contact_hours,
        independent_hours=independent_hours,
        assessment_type=assessment_type,
        is_required=is_required,
        is_active=is_active,
        notes=_normalize_str(notes),
    )
    group_subject.full_clean()
    group_subject.save()
    return group_subject


@transaction.atomic
def update_group_subject(
    *,
    group_subject: GroupSubject,
    **validated_data,
) -> GroupSubject:
    academic_year = validated_data.get("academic_year", group_subject.academic_year)
    period = validated_data.get("period", group_subject.period)

    if period.academic_year_id != academic_year.id:
        raise ValidationError(
            {"period": "Учебный период должен принадлежать тому же учебному году."}
        )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = _normalize_str(value)
        setattr(group_subject, field, value)

    group_subject.full_clean()
    group_subject.save()
    return group_subject


@transaction.atomic
def assign_teacher_group_subject(
    *,
    teacher,
    group_subject: GroupSubject,
    role: str = TeacherGroupSubject.RoleChoices.PRIMARY,
    is_primary: bool = True,
    is_active: bool = True,
    planned_hours: int = 0,
    starts_at=None,
    ends_at=None,
    notes: str = "",
) -> TeacherGroupSubject:
    if not _user_has_teacher_role(teacher):
        raise ValidationError(
            {"teacher": "Закрепление за предметом группы можно создать только для преподавателя."}
        )

    group = group_subject.group
    subject = group_subject.subject

    has_active_org_link = TeacherOrganization.objects.filter(
        teacher=teacher,
        organization=group.organization,
        is_active=True,
    ).exists()

    if not has_active_org_link:
        raise ValidationError(
            {"teacher": "Преподаватель не связан с организацией этой группы."}
        )

    has_active_subject_link = TeacherSubject.objects.filter(
        teacher=teacher,
        subject=subject,
        is_active=True,
    ).exists()

    if not has_active_subject_link:
        raise ValidationError(
            {"teacher": "Преподаватель не закреплён за данным предметом."}
        )

    assignment, created = TeacherGroupSubject.objects.get_or_create(
        teacher=teacher,
        group_subject=group_subject,
        defaults={
            "role": role,
            "is_primary": is_primary,
            "is_active": is_active,
            "planned_hours": planned_hours,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "notes": _normalize_str(notes),
        },
    )

    if not created:
        assignment.role = role
        assignment.is_primary = is_primary
        assignment.is_active = is_active
        assignment.planned_hours = planned_hours
        assignment.starts_at = starts_at
        assignment.ends_at = ends_at
        assignment.notes = _normalize_str(notes)

    if is_primary:
        TeacherGroupSubject.objects.exclude(pk=assignment.pk).filter(
            group_subject=group_subject,
            is_primary=True,
        ).update(is_primary=False)

    assignment.full_clean()
    assignment.save()
    return assignment


@transaction.atomic
def remove_teacher_group_subject(
    *,
    teacher,
    group_subject: GroupSubject,
) -> None:
    TeacherGroupSubject.objects.filter(
        teacher=teacher,
        group_subject=group_subject,
    ).delete()
