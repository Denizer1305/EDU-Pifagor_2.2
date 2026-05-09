from __future__ import annotations

from apps.course.models import CourseAssignment
from apps.course.tests.factories.common import (
    _unwrap_factory_result,
    assignment_counter,
)
from apps.course.tests.factories.course import (
    create_course,
    create_course_with_context,
)
from apps.course.tests.factories.users import create_course_student


def create_course_assignment(
    *,
    course=None,
    group=None,
    student=None,
    assignment_type: str | None = None,
    assigned_by=None,
    starts_at=None,
    ends_at=None,
    is_active: bool = True,
    auto_enroll: bool = True,
    notes: str = "",
):
    """Создаёт тестовое назначение курса группе или студенту."""

    if course is None:
        course = create_course()

    if assigned_by is None:
        assigned_by = course.author

    assigned_by = _unwrap_factory_result(assigned_by)

    if student is not None:
        student = _unwrap_factory_result(student)

    if assignment_type is None:
        assignment_type = (
            CourseAssignment.AssignmentTypeChoices.GROUP
            if group is not None
            else CourseAssignment.AssignmentTypeChoices.STUDENT
        )

    if (
        assignment_type == CourseAssignment.AssignmentTypeChoices.GROUP
        and group is None
    ):
        context = create_course_with_context(author=course.author)
        course = context["course"]
        group = context["group"]

    if (
        assignment_type == CourseAssignment.AssignmentTypeChoices.STUDENT
        and student is None
    ):
        student = create_course_student()

    assignment = CourseAssignment(
        course=course,
        assignment_type=assignment_type,
        group=group,
        student=student,
        assigned_by=assigned_by,
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=is_active,
        auto_enroll=auto_enroll,
        notes=notes or f"Назначение {next(assignment_counter)}",
    )
    assignment.full_clean()
    assignment.save()
    return assignment
