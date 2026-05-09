from __future__ import annotations

from datetime import date

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import ScheduleStatus, Weekday
from apps.schedule.tests.factories import (
    create_schedule_change,
    create_scheduled_lesson,
)

from .base import ScheduleAPIBaseTestCase, ids


class ScheduleChangeAPITestCase(ScheduleAPIBaseTestCase):
    def test_change_list_returns_changes(self):
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

        lesson.status = ScheduleStatus.DRAFT
        lesson.save(update_fields=("status", "updated_at"))

        change = create_schedule_change(scheduled_lesson=lesson)

        response = self.client.get(reverse("schedule:change-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(change.id, ids(response))

    def test_change_detail_returns_change(self):
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

        change = create_schedule_change(scheduled_lesson=lesson)

        response = self.client.get(
            reverse("schedule:change-detail", kwargs={"pk": change.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], change.id)
