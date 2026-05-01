from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import Submission
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_publication,
    create_grade_record,
    create_student_user,
    create_submission,
    create_teacher_user,
)


class RubricAndGradeApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.assignment = create_assignment(author=self.teacher)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            published_by=self.teacher,
        )
        self.submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
        )

    def test_teacher_can_create_rubric(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse("assignments:rubric-list-create"),
            {
                "title": "Рубрика проверки",
                "description": "Критерии",
                "assignment_kind": "essay",
                "is_template": True,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Рубрика проверки")

    def test_teacher_can_create_grade_from_submission(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:grade-create-from-submission",
                kwargs={"submission_id": self.submission.id},
            ),
            {"is_final": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["submission_id"], self.submission.id)

    def test_student_can_view_own_grade(self):
        grade = create_grade_record(
            submission=self.submission,
            graded_by=self.teacher,
        )

        self.client.force_authenticate(self.student)
        response = self.client.get(
            reverse("assignments:grade-detail", kwargs={"pk": grade.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student"]["id"], self.student.id)
