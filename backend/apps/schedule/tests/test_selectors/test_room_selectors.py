from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import RoomType
from apps.schedule.selectors import (
    get_active_rooms,
    get_room_by_id,
    get_room_queryset,
    get_rooms_by_type,
    get_rooms_for_organization,
)
from apps.schedule.tests.factories import (
    create_organization,
    create_schedule_room,
)

from . import ids


class RoomSelectorsTestCase(TestCase):
    def test_room_queryset_contains_rooms(self):
        room = create_schedule_room()

        self.assertIn(room.id, ids(get_room_queryset()))

    def test_get_room_by_id_returns_room(self):
        room = create_schedule_room()

        self.assertEqual(get_room_by_id(room_id=room.id), room)

    def test_get_active_rooms_filters_by_active_and_organization(self):
        organization = create_organization()
        other_organization = create_organization()

        active_room = create_schedule_room(
            organization=organization,
            is_active=True,
        )
        inactive_room = create_schedule_room(
            organization=organization,
            is_active=False,
        )
        other_room = create_schedule_room(
            organization=other_organization,
            is_active=True,
        )

        result = get_active_rooms(organization_id=organization.id)

        self.assertIn(active_room.id, ids(result))
        self.assertNotIn(inactive_room.id, ids(result))
        self.assertNotIn(other_room.id, ids(result))

    def test_get_rooms_for_organization_filters_by_organization(self):
        organization = create_organization()
        other_organization = create_organization()

        room = create_schedule_room(organization=organization)
        other_room = create_schedule_room(organization=other_organization)

        result = get_rooms_for_organization(organization_id=organization.id)

        self.assertIn(room.id, ids(result))
        self.assertNotIn(other_room.id, ids(result))

    def test_get_rooms_by_type_filters_by_room_type_and_active(self):
        organization = create_organization()

        classroom = create_schedule_room(
            organization=organization,
            room_type=RoomType.CLASSROOM,
            is_active=True,
        )
        inactive_classroom = create_schedule_room(
            organization=organization,
            room_type=RoomType.CLASSROOM,
            is_active=False,
        )
        lab = create_schedule_room(
            organization=organization,
            room_type=RoomType.LABORATORY,
            is_active=True,
        )

        result = get_rooms_by_type(
            organization_id=organization.id,
            room_type=RoomType.CLASSROOM,
        )

        self.assertIn(classroom.id, ids(result))
        self.assertNotIn(inactive_classroom.id, ids(result))
        self.assertNotIn(lab.id, ids(result))

        result_with_inactive = get_rooms_by_type(
            organization_id=organization.id,
            room_type=RoomType.CLASSROOM,
            active_only=False,
        )

        self.assertIn(classroom.id, ids(result_with_inactive))
        self.assertIn(inactive_classroom.id, ids(result_with_inactive))
