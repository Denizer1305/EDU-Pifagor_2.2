from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import AssignmentSection
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_question,
    create_teacher_user,
)


class AssignmentStructureApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.assignment = create_assignment(author=self.teacher)

    def test_teacher_can_create_variant(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-variant-list-create",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {
                "title": "Вариант 1",
                "code": "VAR-1",
                "variant_number": 1,
                "order": 1,
                "is_default": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Вариант 1")

    def test_teacher_can_create_section(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-section-list-create",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {
                "title": "Часть А",
                "section_type": AssignmentSection.SectionTypeChoices.choices[0][0],
                "order": 1,
                "max_score": "10",
                "is_required": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Часть А")

    def test_teacher_can_create_question(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-question-list-create",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {
                "question_type": "single_choice",
                "prompt": "2+2=?",
                "answer_options_json": [{"id": "a", "text": "4"}],
                "correct_answer_json": {"id": "a"},
                "max_score": "1",
                "order": 1,
                "is_required": True,
                "requires_manual_review": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["prompt"], "2+2=?")

    def test_teacher_can_reorder_questions(self):
        q1 = create_assignment_question(assignment=self.assignment, order=1)
        q2 = create_assignment_question(assignment=self.assignment, order=2)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse(
                "assignments:assignment-question-reorder",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {"question_ids": [q2.id, q1.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], q2.id)
