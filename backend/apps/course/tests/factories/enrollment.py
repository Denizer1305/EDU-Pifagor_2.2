from __future__ import annotations

from django.utils import timezone

from apps.course.models import CourseEnrollment
from apps.course.tests.factories.common import (
    _unwrap_factory_result,
    enrollment_counter,
)
from apps.course.tests.factories.course import create_course
from apps.course.tests.factories.users import create_course_student


def create_course_enrollment(
    *,
    course=None,
    student=None,
    assignment=None,
    status: str = CourseEnrollment.StatusChoices.ENROLLED,
    progress_percent: int = 0,
    enrolled_at=None,
    started_at=None,
    completed_at=None,
    last_activity_at=None,
):
    """Создаёт тестовое зачисление студента на курс."""

    index = next(enrollment_counter)

    if course is None:
        course = create_course()

    if student is None:
        student = create_course_student(
            email=f"enrollment_student_{index}@example.com"
        )

    student = _unwrap_factory_result(student)

    if enrolled_at is None:
        enrolled_at = timezone.now()

    if status == CourseEnrollment.StatusChoices.IN_PROGRESS and started_at is None:
        started_at = timezone.now()

    if status == CourseEnrollment.StatusChoices.COMPLETED:
        if started_at is None:
            started_at = timezone.now()

        if completed_at is None:
            completed_at = timezone.now()

        progress_percent = 100

    enrollment = CourseEnrollment(
        course=course,
        student=student,
        assignment=assignment,
        status=status,
        progress_percent=progress_percent,
        enrolled_at=enrolled_at,
        started_at=started_at,
        completed_at=completed_at,
        last_activity_at=last_activity_at,
    )
    enrollment.full_clean()
    enrollment.save()
    return enrollment
