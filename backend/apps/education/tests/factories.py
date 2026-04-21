from __future__ import annotations

from datetime import date
from itertools import count

from django.utils import timezone

from apps.education.models import (
    AcademicYear,
    Curriculum,
    CurriculumItem,
    EducationPeriod,
    GroupSubject,
    StudentGroupEnrollment,
    TeacherGroupSubject,
)
from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_organization,
    create_subject,
    create_teacher_organization,
    create_teacher_subject,
)
from apps.users.tests.factories import (
    create_student_user as base_create_student_user,
    create_teacher_user as base_create_teacher_user,
)


academic_year_counter = count(1)
education_period_counter = count(1)
curriculum_counter = count(1)
student_counter = count(1)
teacher_counter = count(1)


def create_academic_year(
    *,
    name: str | None = None,
    start_date=date(2025, 9, 1),
    end_date=date(2026, 6, 30),
    is_current: bool = False,
    is_active: bool = True,
):
    index = next(academic_year_counter)

    if name is None:
        start_year = 2024 + index
        end_year = start_year + 1
        name = f"{start_year}/{end_year}"

    return AcademicYear.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        is_active=is_active,
    )


def create_education_period(
    *,
    academic_year=None,
    name: str | None = None,
    code: str | None = None,
    period_type=EducationPeriod.PeriodTypeChoices.SEMESTER,
    sequence: int = 1,
    start_date=date(2025, 9, 1),
    end_date=date(2025, 12, 31),
    is_current: bool = False,
    is_active: bool = True,
):
    index = next(education_period_counter)

    if academic_year is None:
        academic_year = create_academic_year()

    if name is None:
        name = f"Период {index}"
    if code is None:
        code = f"PERIOD-{index}"

    return EducationPeriod.objects.create(
        academic_year=academic_year,
        name=name,
        code=code,
        period_type=period_type,
        sequence=sequence,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        is_active=is_active,
    )


def _activate_student_user(user):
    user.is_email_verified = True
    user.onboarding_status = "active"
    user.onboarding_completed_at = timezone.now()
    user.save(
        update_fields=(
            "is_email_verified",
            "onboarding_status",
            "onboarding_completed_at",
        )
    )

    if hasattr(user, "student_profile") and user.student_profile:
        user.student_profile.verification_status = "approved"
        user.student_profile.verified_at = timezone.now()
        update_fields = ["verification_status", "verified_at"]
        if hasattr(user.student_profile, "updated_at"):
            update_fields.append("updated_at")
        user.student_profile.save(update_fields=update_fields)

    return user


def _activate_teacher_user(user):
    user.is_email_verified = True
    user.onboarding_status = "active"
    user.onboarding_completed_at = timezone.now()
    user.save(
        update_fields=(
            "is_email_verified",
            "onboarding_status",
            "onboarding_completed_at",
        )
    )

    if hasattr(user, "teacher_profile") and user.teacher_profile:
        user.teacher_profile.verification_status = "approved"
        user.teacher_profile.verified_at = timezone.now()
        update_fields = ["verification_status", "verified_at"]
        if hasattr(user.teacher_profile, "updated_at"):
            update_fields.append("updated_at")
        user.teacher_profile.save(update_fields=update_fields)

    return user


def create_student_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    index = next(student_counter)

    if email is None:
        email = f"student_{index}@example.com"

    created = base_create_student_user(
        email=email,
        password=password,
    )
    user = created[0] if isinstance(created, tuple) else created
    return _activate_student_user(user)


def create_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    index = next(teacher_counter)

    if email is None:
        email = f"teacher_{index}@example.com"

    created = base_create_teacher_user(
        email=email,
        password=password,
    )
    user = created[0] if isinstance(created, tuple) else created
    return _activate_teacher_user(user)


def create_student_group_enrollment(
    *,
    student=None,
    group=None,
    academic_year=None,
    enrollment_date=date(2025, 9, 1),
    completion_date=None,
    status=StudentGroupEnrollment.StatusChoices.ACTIVE,
    is_primary: bool = True,
    journal_number: int | None = 1,
):
    if student is None:
        student = create_student_user()
    if group is None:
        group = create_group()
    if academic_year is None:
        academic_year = create_academic_year()

    return StudentGroupEnrollment.objects.create(
        student=student,
        group=group,
        academic_year=academic_year,
        enrollment_date=enrollment_date,
        completion_date=completion_date,
        status=status,
        is_primary=is_primary,
        journal_number=journal_number,
    )


def create_group_subject(
    *,
    group=None,
    subject=None,
    academic_year=None,
    period=None,
    planned_hours: int = 72,
    contact_hours: int = 48,
    independent_hours: int = 24,
    assessment_type=GroupSubject.AssessmentTypeChoices.EXAM,
    is_required: bool = True,
    is_active: bool = True,
):
    if academic_year is None:
        academic_year = create_academic_year()
    if period is None:
        period = create_education_period(
            academic_year=academic_year,
            start_date=academic_year.start_date,
            end_date=date(2025, 12, 31),
        )
    if group is None:
        group = create_group()
    if subject is None:
        subject = create_subject()

    return GroupSubject.objects.create(
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
    )


def create_teacher_group_subject(
    *,
    teacher=None,
    group_subject=None,
    role=TeacherGroupSubject.RoleChoices.PRIMARY,
    is_primary: bool = True,
    is_active: bool = True,
    planned_hours: int = 72,
    starts_at=date(2025, 9, 1),
    ends_at=date(2025, 12, 31),
):
    if teacher is None:
        teacher = create_teacher_user()
    if group_subject is None:
        group_subject = create_group_subject()

    create_teacher_organization(
        teacher=teacher,
        organization=group_subject.group.organization,
        is_primary=True,
        is_active=True,
    )
    create_teacher_subject(
        teacher=teacher,
        subject=group_subject.subject,
        is_primary=True,
        is_active=True,
    )

    return TeacherGroupSubject.objects.create(
        teacher=teacher,
        group_subject=group_subject,
        role=role,
        is_primary=is_primary,
        is_active=is_active,
        planned_hours=planned_hours,
        starts_at=starts_at,
        ends_at=ends_at,
    )


def create_curriculum(
    *,
    organization=None,
    department=None,
    academic_year=None,
    code: str | None = None,
    name: str | None = None,
    total_hours: int | None = 144,
    is_active: bool = True,
):
    index = next(curriculum_counter)

    if organization is None:
        organization = create_organization()
    if academic_year is None:
        academic_year = create_academic_year()
    if department is None:
        department = create_department(organization=organization)
    if code is None:
        code = f"CURR-{index}"
    if name is None:
        name = f"Учебный план {index}"

    return Curriculum.objects.create(
        organization=organization,
        department=department,
        academic_year=academic_year,
        code=code,
        name=name,
        total_hours=total_hours,
        is_active=is_active,
    )


def create_curriculum_item(
    *,
    curriculum=None,
    period=None,
    subject=None,
    sequence: int = 1,
    planned_hours: int = 72,
    contact_hours: int = 48,
    independent_hours: int = 24,
    assessment_type=CurriculumItem.AssessmentTypeChoices.EXAM,
    is_required: bool = True,
    is_active: bool = True,
):
    if curriculum is None:
        curriculum = create_curriculum()
    if period is None:
        period = create_education_period(
            academic_year=curriculum.academic_year,
            start_date=curriculum.academic_year.start_date,
            end_date=date(2025, 12, 31),
        )
    if subject is None:
        subject = create_subject()

    return CurriculumItem.objects.create(
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
    )
