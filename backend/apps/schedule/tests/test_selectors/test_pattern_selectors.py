from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.schedule.constants import ScheduleStatus, Weekday
from apps.schedule.selectors import (
    get_active_patterns,
    get_pattern_by_id,
    get_pattern_queryset,
    get_patterns_active_on_date,
    get_patterns_for_course,
    get_patterns_for_group,
    get_patterns_for_room,
    get_patterns_for_teacher,
    get_patterns_for_weekday,
    get_published_patterns,
)
from apps.schedule.tests.factories import (
    create_organization,
    create_schedule_pattern,
)

from . import ids


class PatternSelectorsTestCase(TestCase):
    def test_pattern_selectors_filter_patterns(self):
        organization = create_organization()

        pattern = create_schedule_pattern(
            organization=organization,
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
            status=ScheduleStatus.PUBLISHED,
            is_active=True,
        )
        inactive_pattern = create_schedule_pattern(
            organization=organization,
            weekday=Weekday.TUESDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
            is_active=False,
        )

        self.assertIn(pattern.id, ids(get_pattern_queryset()))
        self.assertEqual(get_pattern_by_id(pattern_id=pattern.id), pattern)

        self.assertIn(
            pattern.id,
            ids(get_active_patterns(organization_id=organization.id)),
        )
        self.assertNotIn(
            inactive_pattern.id,
            ids(get_active_patterns(organization_id=organization.id)),
        )
        self.assertIn(
            pattern.id,
            ids(get_published_patterns(organization_id=organization.id)),
        )
        self.assertIn(
            pattern.id,
            ids(get_patterns_for_group(group_id=pattern.group_id)),
        )
        self.assertIn(
            pattern.id,
            ids(get_patterns_for_teacher(teacher_id=pattern.teacher_id)),
        )
        self.assertIn(
            pattern.id,
            ids(get_patterns_for_room(room_id=pattern.room_id)),
        )
        self.assertIn(
            pattern.id,
            ids(get_patterns_for_course(course_id=pattern.course_id)),
        )
        self.assertIn(
            pattern.id,
            ids(
                get_patterns_for_weekday(
                    organization_id=organization.id,
                    weekday=Weekday.MONDAY,
                )
            ),
        )
        self.assertIn(
            pattern.id,
            ids(
                get_patterns_active_on_date(
                    organization_id=organization.id,
                    target_date=date(2025, 9, 15),
                )
            ),
        )
        self.assertNotIn(
            pattern.id,
            ids(
                get_patterns_active_on_date(
                    organization_id=organization.id,
                    target_date=date(2025, 10, 15),
                )
            ),
        )
