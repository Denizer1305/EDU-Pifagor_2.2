from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import ScheduleStatus, Weekday
from apps.schedule.models import SchedulePattern
from apps.schedule.tests.factories import create_schedule_pattern

from .base import ScheduleAPIBaseTestCase, ids


class SchedulePatternAPITestCase(ScheduleAPIBaseTestCase):
    def test_pattern_list_returns_patterns(self):
        context = self.create_context()
        pattern = create_schedule_pattern(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
            time_slot=context["time_slot"],
            group=context["group"],
            subject=context["subject"],
            teacher=context["teacher"],
            room=context["room"],
            group_subject=context["group_subject"],
            course=context["course"],
            course_lesson=context["course_lesson"],
        )

        response = self.client.get(reverse("schedule:pattern-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(pattern.id, ids(response))

    def test_pattern_detail_returns_pattern(self):
        context = self.create_context()
        pattern = create_schedule_pattern(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
            time_slot=context["time_slot"],
            group=context["group"],
            subject=context["subject"],
            teacher=context["teacher"],
            room=context["room"],
            group_subject=context["group_subject"],
            course=context["course"],
            course_lesson=context["course_lesson"],
            title="Шаблон занятия",
        )

        response = self.client.get(
            reverse("schedule:pattern-detail", kwargs={"pk": pattern.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], pattern.id)
        self.assertEqual(response.data["title"], "Шаблон занятия")

    def test_pattern_create_creates_pattern(self):
        context = self.create_context()

        payload = {
            "organization": context["organization"].id,
            "academic_year": context["academic_year"].id,
            "education_period": context["education_period"].id,
            "weekday": Weekday.MONDAY,
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
            "title": "API шаблон",
            "status": ScheduleStatus.DRAFT,
            "starts_on": "2025-09-01",
            "ends_on": "2025-12-31",
            "repeat_rule": "",
            "priority": 100,
            "is_active": True,
            "notes": "",
        }

        response = self.client.post(
            reverse("schedule:pattern-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            SchedulePattern.objects.filter(
                organization=context["organization"],
                title="API шаблон",
            ).exists()
        )

    def test_pattern_deactivate_archives_pattern(self):
        context = self.create_context()
        pattern = create_schedule_pattern(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
            time_slot=context["time_slot"],
            group=context["group"],
            subject=context["subject"],
            teacher=context["teacher"],
            room=context["room"],
            group_subject=context["group_subject"],
            course=context["course"],
            course_lesson=context["course_lesson"],
            is_active=True,
        )

        response = self.client.post(
            reverse("schedule:pattern-deactivate", kwargs={"pk": pattern.pk}),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pattern.refresh_from_db()
        self.assertFalse(pattern.is_active)
        self.assertEqual(pattern.status, ScheduleStatus.ARCHIVED)
