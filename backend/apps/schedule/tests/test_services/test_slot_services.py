from __future__ import annotations

from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import EducationLevel
from apps.schedule.models import ScheduleTimeSlot
from apps.schedule.services.slot_services import (
    bulk_create_default_slots,
    create_time_slot,
    update_time_slot,
    validate_slot_time,
)
from apps.schedule.tests.factories import create_organization


class SlotServicesTestCase(TestCase):
    def test_validate_slot_time_allows_correct_time_range(self):
        validate_slot_time(
            starts_at=time(9, 0),
            ends_at=time(10, 30),
        )

    def test_validate_slot_time_raises_error_if_end_is_before_start(self):
        with self.assertRaises(ValidationError):
            validate_slot_time(
                starts_at=time(10, 30),
                ends_at=time(9, 0),
            )

    def test_validate_slot_time_raises_error_if_times_are_equal(self):
        with self.assertRaises(ValidationError):
            validate_slot_time(
                starts_at=time(9, 0),
                ends_at=time(9, 0),
            )

    def test_create_time_slot_creates_slot_and_calculates_duration(self):
        organization = create_organization()

        slot = create_time_slot(
            organization=organization,
            name="  1 пара  ",
            number=1,
            starts_at=time(8, 30),
            ends_at=time(10, 0),
            education_level=EducationLevel.SPO,
            is_pair=True,
            notes="  Основной слот  ",
        )

        self.assertIsInstance(slot, ScheduleTimeSlot)
        self.assertEqual(slot.organization, organization)
        self.assertEqual(slot.name, "1 пара")
        self.assertEqual(slot.number, 1)
        self.assertEqual(slot.starts_at, time(8, 30))
        self.assertEqual(slot.ends_at, time(10, 0))
        self.assertEqual(slot.duration_minutes, 90)
        self.assertEqual(slot.education_level, EducationLevel.SPO)
        self.assertTrue(slot.is_pair)
        self.assertEqual(slot.notes, "Основной слот")
        self.assertTrue(slot.is_active)

    def test_create_time_slot_uses_explicit_duration_if_passed(self):
        organization = create_organization()

        slot = create_time_slot(
            organization=organization,
            name="1 урок",
            number=1,
            starts_at=time(8, 30),
            ends_at=time(9, 15),
            duration_minutes=40,
        )

        self.assertEqual(slot.duration_minutes, 40)

    def test_create_time_slot_raises_error_for_invalid_time_range(self):
        organization = create_organization()

        with self.assertRaises(ValidationError):
            create_time_slot(
                organization=organization,
                name="Некорректный слот",
                number=1,
                starts_at=time(10, 0),
                ends_at=time(9, 0),
            )

    def test_update_time_slot_updates_fields_and_recalculates_duration(self):
        organization = create_organization()
        slot = create_time_slot(
            organization=organization,
            name="1 пара",
            number=1,
            starts_at=time(8, 30),
            ends_at=time(10, 0),
            duration_minutes=90,
        )

        updated_slot = update_time_slot(
            slot=slot,
            name="  2 пара  ",
            number=2,
            starts_at=time(10, 10),
            ends_at=time(11, 40),
            education_level=EducationLevel.SPO,
            is_pair=True,
            notes="  После перемены  ",
            is_active=False,
        )

        self.assertEqual(updated_slot.pk, slot.pk)
        self.assertEqual(updated_slot.name, "2 пара")
        self.assertEqual(updated_slot.number, 2)
        self.assertEqual(updated_slot.starts_at, time(10, 10))
        self.assertEqual(updated_slot.ends_at, time(11, 40))
        self.assertEqual(updated_slot.duration_minutes, 90)
        self.assertEqual(updated_slot.education_level, EducationLevel.SPO)
        self.assertTrue(updated_slot.is_pair)
        self.assertEqual(updated_slot.notes, "После перемены")
        self.assertFalse(updated_slot.is_active)

    def test_update_time_slot_keeps_explicit_duration_if_passed(self):
        organization = create_organization()
        slot = create_time_slot(
            organization=organization,
            name="1 урок",
            number=1,
            starts_at=time(8, 30),
            ends_at=time(9, 15),
        )

        updated_slot = update_time_slot(
            slot=slot,
            starts_at=time(8, 0),
            ends_at=time(9, 0),
            duration_minutes=45,
        )

        self.assertEqual(updated_slot.duration_minutes, 45)

    def test_update_time_slot_raises_error_for_invalid_time_range(self):
        organization = create_organization()
        slot = create_time_slot(
            organization=organization,
            name="1 пара",
            number=1,
            starts_at=time(8, 30),
            ends_at=time(10, 0),
        )

        with self.assertRaises(ValidationError):
            update_time_slot(
                slot=slot,
                ends_at=time(8, 0),
            )

    def test_bulk_create_default_slots_creates_all_slots(self):
        organization = create_organization()

        slots = bulk_create_default_slots(
            organization=organization,
            education_level=EducationLevel.SPO,
            is_pair=True,
            slots_data=[
                {
                    "name": "1 пара",
                    "number": 1,
                    "starts_at": time(8, 30),
                    "ends_at": time(10, 0),
                },
                {
                    "name": "2 пара",
                    "number": 2,
                    "starts_at": time(10, 10),
                    "ends_at": time(11, 40),
                    "notes": "После перемены",
                },
            ],
        )

        self.assertEqual(len(slots), 2)
        self.assertEqual(ScheduleTimeSlot.objects.count(), 2)
        self.assertEqual(slots[0].education_level, EducationLevel.SPO)
        self.assertEqual(slots[1].education_level, EducationLevel.SPO)
        self.assertTrue(slots[0].is_pair)
        self.assertTrue(slots[1].is_pair)
        self.assertEqual(slots[1].notes, "После перемены")
