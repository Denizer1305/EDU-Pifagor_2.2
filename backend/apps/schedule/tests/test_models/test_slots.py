from __future__ import annotations

from datetime import time

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.schedule.constants import EducationLevel
from apps.schedule.tests.factories import create_organization, create_schedule_time_slot


class ScheduleTimeSlotModelTestCase(TestCase):
    def test_str_contains_number_and_time_range(self):
        slot = create_schedule_time_slot(
            number=1,
            starts_at=time(8, 30),
            ends_at=time(9, 15),
        )

        self.assertIn("1", str(slot))
        self.assertIn("08:30", str(slot))
        self.assertIn("09:15", str(slot))

    def test_ends_at_must_be_after_starts_at(self):
        slot = create_schedule_time_slot()
        slot.starts_at = time(10, 0)
        slot.ends_at = time(9, 0)

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_unique_organization_number_education_level(self):
        organization = create_organization()

        create_schedule_time_slot(
            organization=organization,
            number=1,
            education_level=EducationLevel.MIXED,
        )

        with self.assertRaises(IntegrityError):
            create_schedule_time_slot(
                organization=organization,
                number=1,
                education_level=EducationLevel.MIXED,
            )

    def test_same_number_allowed_for_different_education_levels(self):
        organization = create_organization()

        first_slot = create_schedule_time_slot(
            organization=organization,
            number=1,
            education_level=EducationLevel.SCHOOL,
        )
        second_slot = create_schedule_time_slot(
            organization=organization,
            number=1,
            education_level=EducationLevel.SPO,
        )

        self.assertNotEqual(first_slot.education_level, second_slot.education_level)
