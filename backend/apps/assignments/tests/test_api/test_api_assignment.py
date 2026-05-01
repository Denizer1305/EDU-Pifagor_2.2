from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_question,
    create_student_user,
    create_teacher_user,
)


class AssignmentApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()

    def test_teacher_can_create_assignment(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse("assignments:assignment-list-create"),
            {
                "title": "Контрольная по математике",
                "assignment_kind": "test",
                "control_scope": "current_control",
                "visibility": "assigned_only",
                "education_level": "school",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Контрольная по математике")

    def test_teacher_can_list_assignments(self):
        create_assignment(author=self.teacher, title="Моя работа")
        create_assignment(title="Чужая работа")

        self.client.force_authenticate(self.teacher)
        response = self.client.get(reverse("assignments:assignment-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Моя работа")

    def test_student_cannot_create_assignment(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse("assignments:assignment-list-create"),
            {
                "title": "Нельзя",
                "assignment_kind": "test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_publish_assignment(self):
        assignment = create_assignment(author=self.teacher)
        create_assignment_question(assignment=assignment)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse("assignments:assignment-publish", kwargs={"pk": assignment.id}),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], assignment.StatusChoices.PUBLISHED)

    def test_teacher_can_duplicate_assignment(self):
        assignment = create_assignment(author=self.teacher)
        create_assignment_question(assignment=assignment)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse("assignments:assignment-duplicate", kwargs={"pk": assignment.id}),
            {"title": "Копия"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Копия")
