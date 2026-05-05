from __future__ import annotations

from datetime import date

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import ScheduleStatus, Weekday
from apps.schedule.models import ScheduledLesson
from apps.schedule.tests.factories import create_scheduled_lesson

from .base import ScheduleAPIBaseTestCase, ids


class ScheduledLessonAPITestCase(ScheduleAPIBaseTestCase):
    def test_lesson_list_returns_lessons(self):
        context = self.create_context()
        lesson = create_scheduled_lesson(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
            date=date(2025, 9, 1),
            weekday=Weekday.MONDAY,
            time_slot=context["time_slot"],
            starts_at=context["time_slot"].starts_at,
            ends_at=context["time_slot"].ends_at,
            group=context["group"],
            subject=context["subject"],
            teacher=context["teacher"],
            room=context["room"],
            group_subject=context["group_subject"],
            course=context["course"],
            course_lesson=context["course_lesson"],
            title="Занятие из API теста",
        )

        response = self.client.get(reverse("schedule:lesson-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(lesson.id, ids(response))

    def test_lesson_detail_returns_lesson(self):
        context = self.create_context()
        lesson = create_scheduled_lesson(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
            date=date(2025, 9, 1),
            weekday=Weekday.MONDAY,
            time_slot=context["time_slot"],
            starts_at=context["time_slot"].starts_at,
            ends_at=context["time_slot"].ends_at,
            group=context["group"],
            subject=context["subject"],
            teacher=context["teacher"],
            room=context["room"],
            group_subject=context["group_subject"],
            course=context["course"],
            course_lesson=context["course_lesson"],
            title="Детальное занятие",
        )

        response = self.client.get(
            reverse("schedule:lesson-detail", kwargs={"pk": lesson.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], lesson.id)
        self.assertEqual(response.data["title"], "Детальное занятие")

    def test_lesson_create_creates_lesson(self):
        context = self.create_context()

        payload = {
            "organization": context["organization"].id,
            "academic_year": context["academic_year"].id,
            "education_period": context["education_period"].id,
            "date": "2025-09-02",
            "weekday": Weekday.TUESDAY,
            "time_slot": context["time_slot"].id,
            "starts_at": "09:00:00",
            "ends_at": "10:30:00",
            "group": context["group"].id,
            "subject": context["subject"].id,
            "teacher": context["teacher"].id,
            "room": context["room"].id,
            "group_subject": context["group_subject"].id,
            "course": context["course"].id,
            "course_lesson": context["course_lesson"].id,
            "title": "API занятие",
            "planned_topic": "Тема API занятия",
            "status": ScheduleStatus.DRAFT,
            "is_locked": False,
            "is_public": False,
            "notes": "",
        }

        response = self.client.post(
            reverse("schedule:lesson-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ScheduledLesson.objects.filter(
                organization=context["organization"],
                title="API занятие",
                date=date(2025, 9, 2),
            ).exists()
        )

    def test_lesson_update_changes_title(self):
        context = self.create_context()
        lesson = create_scheduled_lesson(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
            date=date(2025, 9, 1),
            weekday=Weekday.MONDAY,
            time_slot=context["time_slot"],
            starts_at=context["time_slot"].starts_at,
            ends_at=context["time_slot"].ends_at,
            group=context["group"],
            subject=context["subject"],
            teacher=context["teacher"],
            room=context["room"],
            group_subject=context["group_subject"],
            course=context["course"],
            course_lesson=context["course_lesson"],
            title="Старое название",
        )

        response = self.client.patch(
            reverse("schedule:lesson-detail", kwargs={"pk": lesson.pk}),
            {"title": "Новое название"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        lesson.refresh_from_db()
        self.assertEqual(lesson.title, "Новое название")
