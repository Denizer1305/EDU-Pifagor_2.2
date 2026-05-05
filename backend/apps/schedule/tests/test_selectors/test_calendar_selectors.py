from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import EducationLevel
from apps.schedule.selectors import (
    get_active_time_slots,
    get_time_slot_by_id,
    get_time_slot_queryset,
    get_time_slots_by_education_level,
    get_time_slots_for_organization,
)
from apps.schedule.tests.factories import (
    create_organization,
    create_schedule_time_slot,
)

from . import ids


class SlotSelectorsTestCase(TestCase):
    def test_time_slot_queryset_contains_slots(self):
        slot = create_schedule_time_slot()

        self.assertIn(slot.id, ids(get_time_slot_queryset()))

    def test_get_time_slot_by_id_returns_slot(self):
        slot = create_schedule_time_slot()

        self.assertEqual(get_time_slot_by_id(time_slot_id=slot.id), slot)

    def test_get_active_time_slots_filters_by_active_and_organization(self):
        organization = create_organization()
        other_organization = create_organization()

        active_slot = create_schedule_time_slot(
            organization=organization,
            is_active=True,
        )
        inactive_slot = create_schedule_time_slot(
            organization=organization,
            is_active=False,
        )
        other_slot = create_schedule_time_slot(
            organization=other_organization,
            is_active=True,
        )

        result = get_active_time_slots(organization_id=organization.id)

        self.assertIn(active_slot.id, ids(result))
        self.assertNotIn(inactive_slot.id, ids(result))
        self.assertNotIn(other_slot.id, ids(result))

    def test_get_time_slots_for_organization_filters_active_by_default(self):
        organization = create_organization()

        active_slot = create_schedule_time_slot(
            organization=organization,
            is_active=True,
        )
        inactive_slot = create_schedule_time_slot(
            organization=organization,
            is_active=False,
        )

        result = get_time_slots_for_organization(
            organization_id=organization.id,
        )

        self.assertIn(active_slot.id, ids(result))
        self.assertNotIn(inactive_slot.id, ids(result))

        result_with_inactive = get_time_slots_for_organization(
            organization_id=organization.id,
            active_only=False,
        )

        self.assertIn(active_slot.id, ids(result_with_inactive))
        self.assertIn(inactive_slot.id, ids(result_with_inactive))

    def test_get_time_slots_by_education_level_filters_by_level(self):
        organization = create_organization()

        spo_slot = create_schedule_time_slot(
            organization=organization,
            education_level=EducationLevel.SPO,
            is_active=True,
        )
        school_slot = create_schedule_time_slot(
            organization=organization,
            education_level=EducationLevel.SCHOOL,
            is_active=True,
        )

        result = get_time_slots_by_education_level(
            organization_id=organization.id,
            education_level=EducationLevel.SPO,
        )

        self.assertIn(spo_slot.id, ids(result))
        self.assertNotIn(school_slot.id, ids(result))
