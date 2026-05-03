from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.journal.models.choices import AttendanceStatus, JournalLessonStatus
from apps.journal.services.summary_services import recalculate_journal_summary
from apps.journal.tests.factories import (
    create_attendance_record,
    create_five_point_grade,
    create_journal_lesson,
    create_student_user,
    create_user,
)


class JournalApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_lesson_list(self):
        create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        response = self.client.get(reverse("journal:lesson-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_detail(self):
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        response = self.client.get(
            reverse("journal:lesson-detail", kwargs={"pk": lesson.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attendance_list(self):
        create_attendance_record(status=AttendanceStatus.PRESENT)

        response = self.client.get(reverse("journal:attendance-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attendance_detail(self):
        attendance = create_attendance_record(status=AttendanceStatus.PRESENT)

        response = self.client.get(
            reverse("journal:attendance-detail", kwargs={"pk": attendance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_grade_list(self):
        create_five_point_grade(score=5)

        response = self.client.get(reverse("journal:grade-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_grade_detail(self):
        grade = create_five_point_grade(score=5)

        response = self.client.get(
            reverse("journal:grade-detail", kwargs={"pk": grade.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_summary_list(self):
        student = create_student_user()
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        recalculate_journal_summary(
            course_id=lesson.course_id,
            group_id=lesson.group_id,
            student_id=student.id,
        )

        response = self.client.get(reverse("journal:summary-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_summary_recalculate(self):
        student = create_student_user()
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        response = self.client.post(
            reverse("journal:summary-recalculate"),
            data={
                "course_id": lesson.course_id,
                "group_id": lesson.group_id,
                "student_id": student.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["course"], lesson.course_id)
        self.assertEqual(response.data["group"], lesson.group_id)

    def test_topic_progress_list(self):
        create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        response = self.client.get(reverse("journal:topic-progress-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_topic_progress_sync(self):
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        response = self.client.post(
            reverse("journal:topic-progress-sync"),
            data={
                "course_id": lesson.course_id,
                "group_id": lesson.group_id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
