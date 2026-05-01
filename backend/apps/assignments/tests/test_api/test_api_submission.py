from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import AssignmentPublication, Submission
from apps.assignments.tests.test_api.api_common import COURSE_ENROLLMENT_AUDIENCE
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_audience,
    create_assignment_policy,
    create_assignment_publication,
    create_assignment_question,
    create_course_enrollment,
    create_student_user,
    create_submission,
    create_teacher_user,
)


class SubmissionApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.course_enrollment = create_course_enrollment(student=self.student)
        self.assignment = create_assignment(
            author=self.teacher,
            course=self.course_enrollment.course,
        )
        create_assignment_policy(self.assignment, attempts_limit=2)
        self.question = create_assignment_question(assignment=self.assignment)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            course=self.course_enrollment.course,
            published_by=self.teacher,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        create_assignment_audience(
            publication=self.publication,
            audience_type=COURSE_ENROLLMENT_AUDIENCE,
            course_enrollment=self.course_enrollment,
        )

    def test_student_can_start_submission(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse("assignments:submission-start"),
            {
                "publication_id": self.publication.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student"]["id"], self.student.id)

    def test_student_can_save_answer(self):
        submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse(
                "assignments:submission-answer-save",
                kwargs={"submission_id": submission.id},
            ),
            {
                "question_id": self.question.id,
                "answer_text": "Мой ответ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], submission.id)

    def test_student_can_submit_submission(self):
        submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse(
                "assignments:submission-submit",
                kwargs={"submission_id": submission.id},
            ),
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Submission.StatusChoices.SUBMITTED)

    def test_student_can_retry_submission(self):
        submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse(
                "assignments:submission-retry",
                kwargs={"submission_id": submission.id},
            ),
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], submission.id)
