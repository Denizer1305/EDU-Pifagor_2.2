from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import RoomType
from apps.schedule.models import ScheduleRoom
from apps.schedule.services.room_services import (
    archive_room,
    create_room,
    update_room,
)
from apps.schedule.tests.factories import create_organization


class RoomServicesTestCase(TestCase):
    def test_create_room_creates_room_and_normalizes_text_fields(self):
        organization = create_organization()

        room = create_room(
            organization=organization,
            name="  Кабинет информатики  ",
            number="  305  ",
            room_type=RoomType.COMPUTER_LAB,
            capacity=25,
            floor="  3  ",
            building="  Главный корпус  ",
            notes="  Есть проектор  ",
        )

        self.assertIsInstance(room, ScheduleRoom)
        self.assertEqual(room.organization, organization)
        self.assertEqual(room.name, "Кабинет информатики")
        self.assertEqual(room.number, "305")
        self.assertEqual(room.room_type, RoomType.COMPUTER_LAB)
        self.assertEqual(room.capacity, 25)
        self.assertEqual(room.floor, "3")
        self.assertEqual(room.building, "Главный корпус")
        self.assertEqual(room.notes, "Есть проектор")
        self.assertTrue(room.is_active)

    def test_create_room_runs_model_validation(self):
        organization = create_organization()

        with self.assertRaises(ValidationError):
            create_room(
                organization=organization,
                name="Кабинет с отрицательной вместимостью",
                number="101",
                capacity=-1,
            )

    def test_update_room_updates_only_passed_fields(self):
        organization = create_organization()
        room = create_room(
            organization=organization,
            name="Старое название",
            number="101",
            room_type=RoomType.CLASSROOM,
            capacity=20,
            floor="1",
            building="А",
            notes="Старые заметки",
        )

        updated_room = update_room(
            room=room,
            name="  Новое название  ",
            number="  202  ",
            room_type=RoomType.LABORATORY,
            capacity=30,
            floor="  2  ",
            building="  Б  ",
            notes="  Новые заметки  ",
            is_active=False,
        )

        self.assertEqual(updated_room.pk, room.pk)
        self.assertEqual(updated_room.name, "Новое название")
        self.assertEqual(updated_room.number, "202")
        self.assertEqual(updated_room.room_type, RoomType.LABORATORY)
        self.assertEqual(updated_room.capacity, 30)
        self.assertEqual(updated_room.floor, "2")
        self.assertEqual(updated_room.building, "Б")
        self.assertEqual(updated_room.notes, "Новые заметки")
        self.assertFalse(updated_room.is_active)

    def test_update_room_keeps_department_when_not_passed(self):
        organization = create_organization()
        room = create_room(
            organization=organization,
            name="Кабинет",
            number="101",
        )

        updated_room = update_room(
            room=room,
            name="Кабинет 101",
        )

        self.assertEqual(updated_room.department, room.department)
        self.assertEqual(updated_room.name, "Кабинет 101")

    def test_archive_room_marks_room_inactive(self):
        organization = create_organization()
        room = create_room(
            organization=organization,
            name="Кабинет",
            number="101",
            is_active=True,
        )

        archived_room = archive_room(room=room)

        self.assertEqual(archived_room.pk, room.pk)
        self.assertFalse(archived_room.is_active)

    def test_archive_room_raises_error_if_room_already_archived(self):
        organization = create_organization()
        room = create_room(
            organization=organization,
            name="Кабинет",
            number="101",
            is_active=False,
        )

        with self.assertRaises(ValidationError):
            archive_room(room=room)
