from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.education.models import AcademicYear, Curriculum, CurriculumItem, EducationPeriod
from apps.organizations.models import Department, Organization, Subject


def _normalize_str(value):
    return value.strip() if isinstance(value, str) else value


@transaction.atomic
def create_curriculum(
    *,
    organization: Organization,
    academic_year: AcademicYear,
    code: str,
    name: str,
    department: Department | None = None,
    description: str = "",
    total_hours: int | None = None,
    is_active: bool = True,
) -> Curriculum:
    if department and department.organization_id != organization.id:
        raise ValidationError(
            {"department": "Подразделение должно принадлежать той же организации, что и учебный план."}
        )

    curriculum = Curriculum(
        organization=organization,
        department=department,
        academic_year=academic_year,
        code=_normalize_str(code),
        name=_normalize_str(name),
        description=_normalize_str(description),
        total_hours=total_hours,
        is_active=is_active,
    )
    curriculum.full_clean()
    curriculum.save()
    return curriculum


@transaction.atomic
def update_curriculum(
    *,
    curriculum: Curriculum,
    **validated_data,
) -> Curriculum:
    organization = validated_data.get("organization", curriculum.organization)
    department = validated_data.get("department", curriculum.department)

    if department and department.organization_id != organization.id:
        raise ValidationError(
            {"department": "Подразделение должно принадлежать той же организации, что и учебный план."}
        )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = _normalize_str(value)
        setattr(curriculum, field, value)

    curriculum.full_clean()
    curriculum.save()
    return curriculum


@transaction.atomic
def create_curriculum_item(
    *,
    curriculum: Curriculum,
    period: EducationPeriod,
    subject: Subject,
    sequence: int = 1,
    planned_hours: int = 0,
    contact_hours: int = 0,
    independent_hours: int = 0,
    assessment_type: str = CurriculumItem.AssessmentTypeChoices.NONE,
    is_required: bool = True,
    is_active: bool = True,
    notes: str = "",
) -> CurriculumItem:
    if period.academic_year_id != curriculum.academic_year_id:
        raise ValidationError(
            {"period": "Учебный период должен принадлежать тому же учебному году, что и учебный план."}
        )

    item = CurriculumItem(
        curriculum=curriculum,
        period=period,
        subject=subject,
        sequence=sequence,
        planned_hours=planned_hours,
        contact_hours=contact_hours,
        independent_hours=independent_hours,
        assessment_type=assessment_type,
        is_required=is_required,
        is_active=is_active,
        notes=_normalize_str(notes),
    )
    item.full_clean()
    item.save()
    return item


@transaction.atomic
def update_curriculum_item(
    *,
    item: CurriculumItem,
    **validated_data,
) -> CurriculumItem:
    curriculum = validated_data.get("curriculum", item.curriculum)
    period = validated_data.get("period", item.period)

    if period.academic_year_id != curriculum.academic_year_id:
        raise ValidationError(
            {"period": "Учебный период должен принадлежать тому же учебному году, что и учебный план."}
        )

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = _normalize_str(value)
        setattr(item, field, value)

    item.full_clean()
    item.save()
    return item
