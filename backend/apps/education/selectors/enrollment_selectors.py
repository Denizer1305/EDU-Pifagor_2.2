from __future__ import annotations

from apps.education.models import StudentGroupEnrollment


def get_student_group_enrollments_queryset():
    return StudentGroupEnrollment.objects.select_related(
        "student",
        "student__profile",
        "group",
        "group__organization",
        "group__department",
        "academic_year",
    ).all()


def get_active_student_group_enrollments_queryset():
    return StudentGroupEnrollment.objects.select_related(
        "student",
        "student__profile",
        "group",
        "group__organization",
        "group__department",
        "academic_year",
    ).filter(
        status=StudentGroupEnrollment.StatusChoices.ACTIVE,
    )


def get_student_enrollments_queryset(*, student_id: int):
    return get_student_group_enrollments_queryset().filter(
        student_id=student_id,
    )


def get_group_enrollments_queryset(*, group_id: int):
    return get_student_group_enrollments_queryset().filter(
        group_id=group_id,
    )
