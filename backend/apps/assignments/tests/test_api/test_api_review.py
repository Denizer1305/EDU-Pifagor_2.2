from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import Submission
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_publication,
    create_assignment_question,
    create_student_user,
    create_submission,
    create_submission_review,
    create_teacher_user,
)


class ReviewApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.assignment = create_assignment(author=self.teacher)
        self.question = create_assignment_question(
            assignment=self.assignment,
            requires_manual_review=True,
        )
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

    def test_teacher_can_start_review(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:submission-review-start",
                kwargs={"submission_id": self.submission.id},
            ),
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submission_id"], self.submission.id)

    def test_teacher_can_view_reviews(self):
        review = create_submission_review(
            submission=self.submission,
            reviewer=self.teacher,
        )

        self.client.force_authenticate(self.teacher)
        response = self.client.get(
            reverse("assignments:submission-review-detail", kwargs={"pk": review.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], review.id)

    def test_teacher_can_create_review_comment(self):
        review = create_submission_review(
            submission=self.submission,
            reviewer=self.teacher,
        )

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse(
                "assignments:review-comment-create",
                kwargs={"review_id": review.id},
            ),
            {
                "comment_type": "general",
                "message": "Нужно подробнее объяснить решение",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["message"],
            "Нужно подробнее объяснить решение",
        )
