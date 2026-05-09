from __future__ import annotations

from datetime import date

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import Weekday
from apps.schedule.tests.factories import create_scheduled_lesson

from .base import ScheduleAPIBaseTestCase


class ScheduleReportAPITestCase(ScheduleAPIBaseTestCase):
    def test_group_report_returns_lessons(self):
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
        )

        response = self.client.get(
            reverse("schedule:report-group"),
            {
                "group": context["group"].id,
                "starts_on": "2025-09-01",
                "ends_on": "2025-09-30",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["lessons_count"], 1)
        self.assertEqual(response.data["lessons"][0]["id"], lesson.id)

    def test_room_report_returns_lessons(self):
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
        )

        response = self.client.get(
            reverse("schedule:report-room"),
            {
                "room": context["room"].id,
                "starts_on": "2025-09-01",
                "ends_on": "2025-09-30",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["lessons_count"], 1)
        self.assertEqual(response.data["lessons"][0]["id"], lesson.id)
