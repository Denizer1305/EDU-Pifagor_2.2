from __future__ import annotations

from django.db.models import Q

from apps.course.models import CourseAssignment, CourseEnrollment


def get_course_assignments_queryset(
    *,
    course_id: int | None = None,
    group_id: int | None = None,
    student_id: int | None = None,
    assignment_type: str = "",
    is_active: bool | None = None,
):
    queryset = CourseAssignment.objects.select_related(
        "course",
        "group",
        "student",
        "assigned_by",
    )

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if group_id:
        queryset = queryset.filter(group_id=group_id)

    if student_id:
        queryset = queryset.filter(student_id=student_id)

    if assignment_type:
        queryset = queryset.filter(assignment_type=assignment_type)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.order_by("-created_at")


def get_course_enrollments_queryset(
    *,
    course_id: int | None = None,
    student_id: int | None = None,
    status: str = "",
    search: str = "",
):
    queryset = CourseEnrollment.objects.select_related(
        "course",
        "student",
        "assignment",
    ).prefetch_related(
        "progress",
    )

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if student_id:
        queryset = queryset.filter(student_id=student_id)

    if status:
        queryset = queryset.filter(status=status)

    if search:
        queryset = queryset.filter(
            Q(course__title__icontains=search)
            | Q(course__code__icontains=search)
            | Q(student__email__icontains=search)
            | Q(student__profile__first_name__icontains=search)
            | Q(student__profile__last_name__icontains=search)
        )

    return queryset.order_by("-created_at")


def get_student_course_enrollments_queryset(*, student_id: int, status: str = ""):
    return get_course_enrollments_queryset(
        student_id=student_id,
        status=status,
    )


def get_course_enrollment_by_id(*, enrollment_id: int):
    return CourseEnrollment.objects.select_related(
        "course",
        "student",
        "assignment",
    ).prefetch_related(
        "progress",
        "lesson_progresses",
    ).filter(id=enrollment_id).first()
