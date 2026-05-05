from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import WeekType
from apps.schedule.tests.factories import create_schedule_week_template

from .base import ScheduleAPIBaseTestCase, ids


class ScheduleWeekTemplateAPITestCase(ScheduleAPIBaseTestCase):
    def test_week_template_list_returns_templates(self):
        context = self.create_context()
        template = create_schedule_week_template(
            organization=context["organization"],
            academic_year=context["academic_year"],
            education_period=context["education_period"],
        )

        response = self.client.get(reverse("schedule:week-template-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(template.id, ids(response))

    def test_week_template_create_creates_template(self):
        context = self.create_context()

        payload = {
            "organization": context["organization"].id,
            "academic_year": context["academic_year"].id,
            "education_period": context["education_period"].id,
            "name": "Числитель",
            "week_type": WeekType.NUMERATOR,
            "starts_on": "2025-09-01",
            "ends_on": "2025-09-07",
            "is_default": False,
            "is_active": True,
            "notes": "",
        }

        response = self.client.post(
            reverse("schedule:week-template-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Числитель")
        self.assertEqual(response.data["week_type"], WeekType.NUMERATOR)
