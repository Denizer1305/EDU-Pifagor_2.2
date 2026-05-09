from __future__ import annotations

from datetime import date

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import ConflictType, Weekday
from apps.schedule.tests.factories import (
    create_schedule_conflict,
    create_scheduled_lesson,
)

from .base import ScheduleAPIBaseTestCase, ids


class ScheduleConflictAPITestCase(ScheduleAPIBaseTestCase):
    def test_conflict_list_returns_conflicts(self):
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
        conflict = create_schedule_conflict(
            organization=context["organization"],
            lesson=lesson,
            conflict_type=ConflictType.GROUP_OVERLAP,
            message="Группа занята",
        )

        response = self.client.get(reverse("schedule:conflict-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(conflict.id, ids(response))

    def test_conflict_detail_returns_conflict(self):
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
        conflict = create_schedule_conflict(
            organization=context["organization"],
            lesson=lesson,
            conflict_type=ConflictType.ROOM_OVERLAP,
            message="Аудитория занята",
        )

        response = self.client.get(
            reverse("schedule:conflict-detail", kwargs={"pk": conflict.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], conflict.id)
        self.assertEqual(response.data["conflict_type"], ConflictType.ROOM_OVERLAP)
