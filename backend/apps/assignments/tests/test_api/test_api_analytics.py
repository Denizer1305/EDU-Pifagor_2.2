from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import AssignmentPublication, Submission
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_publication,
    create_course_enrollment,
    create_student_user,
    create_submission,
    create_teacher_user,
)
from apps.course.tests.factories import create_course


class AnalyticsApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.course = create_course(author=self.teacher)
        self.course_enrollment = create_course_enrollment(
            student=self.student,
            course=self.course,
        )
        self.assignment = create_assignment(author=self.teacher, course=self.course)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            course=self.course,
            published_by=self.teacher,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        self.submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
            final_score=8,
            percentage=80,
            passed=True,
        )

    def test_teacher_can_get_assignment_statistics(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:assignment-statistics",
                kwargs={"assignment_id": self.assignment.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["assignment_id"], self.assignment.id)

    def test_teacher_can_get_publication_statistics(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:publication-statistics",
                kwargs={"publication_id": self.publication.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["publication_id"], self.publication.id)

    def test_teacher_can_get_student_progress(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:student-assignment-progress",
                kwargs={
                    "assignment_id": self.assignment.id,
                    "student_id": self.student.id,
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_id"], self.student.id)

    def test_teacher_can_get_course_dashboard(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:course-assignment-dashboard",
                kwargs={"course_id": self.course_enrollment.course.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["course_id"],
            self.course_enrollment.course.id,
        )
