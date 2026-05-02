from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import AssignmentPublication
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_publication,
    create_course_enrollment,
    create_student_user,
    create_teacher_user,
)
from apps.assignments.tests.test_api.api_common import COURSE_ENROLLMENT_AUDIENCE
from apps.course.tests.factories import create_course


class PublicationAndAudienceApiTestCase(APITestCase):
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
        )

    def test_teacher_can_create_publication(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse("assignments:assignment-publication-list-create"),
            {
                "assignment_id": self.assignment.id,
                "course_id": self.course_enrollment.course.id,
                "title_override": "Итоговая публикация",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title_override"], "Итоговая публикация")

    def test_teacher_can_publish_publication(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-publication-publish",
                kwargs={"pk": self.publication.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"],
            AssignmentPublication.StatusChoices.PUBLISHED,
        )

    def test_teacher_can_assign_student_audience(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-audience-list-create",
                kwargs={"publication_id": self.publication.id},
            ),
            {
                "audience_type": "student",
                "student_id": self.student.id,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student"]["id"], self.student.id)

    def test_teacher_can_assign_course_enrollment(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-audience-list-create",
                kwargs={"publication_id": self.publication.id},
            ),
            {
                "audience_type": COURSE_ENROLLMENT_AUDIENCE,
                "course_enrollment_id": self.course_enrollment.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
