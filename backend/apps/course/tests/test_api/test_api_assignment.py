from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.course.models import CourseEnrollment
from apps.course.tests.factories import (
    create_course_author,
    create_course_enrollment,
    create_course_student,
    create_course_with_context,
)


class CourseAssignmentApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = create_course_author(email="assignment_teacher_api@example.com")
        self.student = create_course_student(email="assignment_student_api@example.com")
        self.context = create_course_with_context(author=self.teacher)
        self.course = self.context["course"]
        self.group = self.context["group"]

    def test_teacher_can_create_group_assignment(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-assignment-list-create", args=[self.course.id])

        response = self.client.post(
            url,
            data={
                "assignment_type": "group",
                "group": self.group.id,
                "auto_enroll": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["assignment_type"], "group")

    def test_teacher_can_list_enrollments(self):
        enrollment = create_course_enrollment(
            course=self.course,
            student=self.student,
        )

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-enrollment-list", args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(enrollment.id, ids)

    def test_student_can_list_own_enrollments(self):
        enrollment = create_course_enrollment(
            course=self.course,
            student=self.student,
        )

        self.client.force_authenticate(user=self.student)
        url = reverse("course:my-course-enrollment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(enrollment.id, ids)

    def test_student_can_cancel_own_enrollment(self):
        enrollment = create_course_enrollment(
            course=self.course,
            student=self.student,
        )

        self.client.force_authenticate(user=self.student)
        url = reverse("course:course-enrollment-cancel", args=[enrollment.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"],
            CourseEnrollment.StatusChoices.CANCELLED,
        )
