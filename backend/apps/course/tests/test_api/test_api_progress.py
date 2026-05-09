from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.course.models import CourseEnrollment
from apps.course.tests.factories import (
    create_course,
    create_course_author,
    create_course_enrollment,
    create_course_lesson,
    create_course_module,
    create_course_progress,
    create_course_student,
)


class CourseProgressApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = create_course_author(email="progress_teacher_api@example.com")
        self.student = create_course_student(email="progress_student_api@example.com")
        self.course = create_course(author=self.teacher)
        self.module = create_course_module(course=self.course)
        self.lesson = create_course_lesson(course=self.course, module=self.module)
        self.enrollment = create_course_enrollment(
            course=self.course,
            student=self.student,
        )
        self.progress = create_course_progress(enrollment=self.enrollment)

    def test_student_can_start_course(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("course:course-enrollment-start", args=[self.enrollment.id])

        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.enrollment.refresh_from_db()
        self.assertEqual(
            self.enrollment.status,
            CourseEnrollment.StatusChoices.IN_PROGRESS,
        )

    def test_student_can_mark_lesson_in_progress(self):
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "course:lesson-progress-in-progress",
            args=[self.enrollment.id, self.lesson.id],
        )

        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in_progress")

    def test_student_can_complete_lesson(self):
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "course:lesson-progress-complete",
            args=[self.enrollment.id, self.lesson.id],
        )

        response = self.client.post(
            url,
            data={
                "spent_minutes": 30,
                "attempts_increment": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_teacher_can_view_course_progress(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-progress-detail", args=[self.enrollment.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["enrollment"], self.enrollment.id)
