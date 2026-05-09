from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.schedule.tests.factories import create_organization, create_schedule_room


class ScheduleRoomModelTestCase(TestCase):
    def test_str_returns_room_name(self):
        room = create_schedule_room(
            name="305",
            building="Корпус А",
            floor="3",
        )

        self.assertEqual(str(room), "305")

    def test_room_unique_inside_same_organization_building_floor(self):
        organization = create_organization()

        create_schedule_room(
            organization=organization,
            name="101",
            building="Главный корпус",
            floor="1",
        )

        with self.assertRaises(IntegrityError):
            create_schedule_room(
                organization=organization,
                name="101",
                building="Главный корпус",
                floor="1",
            )

    def test_same_room_name_allowed_for_different_organizations(self):
        first_organization = create_organization()
        second_organization = create_organization()

        first_room = create_schedule_room(
            organization=first_organization,
            name="101",
            building="Главный корпус",
            floor="1",
        )
        second_room = create_schedule_room(
            organization=second_organization,
            name="101",
            building="Главный корпус",
            floor="1",
        )

        self.assertNotEqual(first_room.organization_id, second_room.organization_id)

    def test_negative_capacity_is_invalid(self):
        room = create_schedule_room(capacity=1)
        room.capacity = -1

        with self.assertRaises(ValidationError):
            room.full_clean()
