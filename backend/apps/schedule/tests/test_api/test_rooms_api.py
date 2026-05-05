from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.schedule.constants import RoomType
from apps.schedule.models import ScheduleRoom
from apps.schedule.tests.factories import create_schedule_room

from .base import ScheduleAPIBaseTestCase, ids


class ScheduleAPIPermissionTestCase(ScheduleAPIBaseTestCase):
    def test_unauthenticated_user_cannot_access_schedule_api(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("schedule:room-list-create"))

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )


class ScheduleRoomAPITestCase(ScheduleAPIBaseTestCase):
    def test_room_list_returns_rooms(self):
        context = self.create_context()
        room = create_schedule_room(organization=context["organization"])

        response = self.client.get(reverse("schedule:room-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(room.id, ids(response))

    def test_room_detail_returns_room(self):
        context = self.create_context()
        room = create_schedule_room(
            organization=context["organization"],
            name="Лаборатория",
            number="401",
            room_type=RoomType.LABORATORY,
        )

        response = self.client.get(
            reverse("schedule:room-detail", kwargs={"pk": room.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], room.id)
        self.assertEqual(response.data["number"], "401")

    def test_room_create_creates_room(self):
        context = self.create_context()

        payload = {
            "organization": context["organization"].id,
            "name": "Компьютерный класс",
            "number": "501",
            "room_type": RoomType.COMPUTER_LAB,
            "capacity": 24,
            "floor": "5",
            "building": "Корпус А",
            "is_active": True,
            "notes": "Есть проектор",
        }

        response = self.client.post(
            reverse("schedule:room-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ScheduleRoom.objects.filter(
                organization=context["organization"],
                number="501",
                building="Корпус А",
            ).exists()
        )
