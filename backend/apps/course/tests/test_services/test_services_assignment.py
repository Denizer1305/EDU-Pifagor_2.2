from __future__ import annotations

from django.test import TestCase

from apps.course.models import CourseEnrollment
from apps.course.services import (
    assign_course_to_group,
    assign_course_to_student,
    cancel_course_enrollment,
    create_course_enrollment,
    remove_course_assignment,
)
from apps.course.tests.factories import (
    create_course as create_course_factory,
)
from apps.course.tests.factories import (
    create_course_student,
    create_course_with_context,
)


class CourseAssignmentServicesTestCase(TestCase):
    def test_assign_course_to_group(self):
        context = create_course_with_context()
        course = context["course"]
        group = context["group"]

        assignment = assign_course_to_group(
            course=course,
            group=group,
            assigned_by=course.author,
        )

        self.assertEqual(assignment.course, course)
        self.assertEqual(assignment.group, group)

    def test_assign_course_to_student(self):
        course = create_course_factory()
        student = create_course_student()

        assignment = assign_course_to_student(
            course=course,
            student=student,
            assigned_by=course.author,
        )

        self.assertEqual(assignment.student, student)

    def test_create_and_cancel_enrollment(self):
        course = create_course_factory()
        student = create_course_student()

        enrollment = create_course_enrollment(
            course=course,
            student=student,
        )

        cancelled = cancel_course_enrollment(enrollment=enrollment)

        self.assertEqual(cancelled.status, CourseEnrollment.StatusChoices.CANCELLED)

    def test_remove_assignment_with_enrollments_only_deactivates(self):
        course = create_course_factory()
        student = create_course_student()

        assignment = assign_course_to_student(
            course=course,
            student=student,
            assigned_by=course.author,
        )
        create_course_enrollment(
            course=course,
            student=student,
            assignment=assignment,
        )

        remove_course_assignment(assignment=assignment)

        assignment.refresh_from_db()
        self.assertFalse(assignment.is_active)
