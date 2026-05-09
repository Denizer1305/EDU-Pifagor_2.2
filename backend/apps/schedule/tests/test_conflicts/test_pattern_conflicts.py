from __future__ import annotations

from datetime import time

from django.test import TestCase

from apps.schedule.constants import ConflictType, ScheduleStatus, Weekday
from apps.schedule.models import ScheduleConflict
from apps.schedule.services.conflict_services import detect_conflicts_for_pattern
from apps.schedule.tests.factories import (
    create_group,
    create_schedule_pattern,
    create_schedule_room,
    create_user,
)


class PatternConflictIntegrationTestCase(TestCase):
    def test_overlapping_patterns_create_teacher_room_and_group_conflicts(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        base_pattern = create_schedule_pattern(
            organization=room.organization,
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            group=group,
            is_active=True,
            status=ScheduleStatus.DRAFT,
        )

        target_pattern = create_schedule_pattern(
            organization=base_pattern.organization,
            academic_year=base_pattern.academic_year,
            education_period=base_pattern.education_period,
            course=base_pattern.course,
            group_subject=base_pattern.group_subject,
            subject=base_pattern.subject,
            group=group,
            weekday=base_pattern.weekday,
            time_slot=base_pattern.time_slot,
            starts_at=time(9, 30),
            ends_at=time(10, 0),
            teacher=teacher,
            room=room,
            is_active=True,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_pattern(target_pattern)
        conflict_types = {conflict.conflict_type for conflict in conflicts}

        self.assertIn(ConflictType.TEACHER_OVERLAP, conflict_types)
        self.assertIn(ConflictType.ROOM_OVERLAP, conflict_types)
        self.assertIn(ConflictType.GROUP_OVERLAP, conflict_types)

        self.assertEqual(
            ScheduleConflict.objects.filter(pattern=target_pattern).count(),
            3,
        )

    def test_pattern_conflict_detection_ignores_inactive_related_patterns(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        inactive_pattern = create_schedule_pattern(
            organization=room.organization,
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            group=group,
            is_active=False,
            status=ScheduleStatus.DRAFT,
        )

        target_pattern = create_schedule_pattern(
            organization=inactive_pattern.organization,
            academic_year=inactive_pattern.academic_year,
            education_period=inactive_pattern.education_period,
            course=inactive_pattern.course,
            group_subject=inactive_pattern.group_subject,
            subject=inactive_pattern.subject,
            group=group,
            weekday=inactive_pattern.weekday,
            starts_at=inactive_pattern.starts_at,
            ends_at=inactive_pattern.ends_at,
            teacher=teacher,
            room=room,
            is_active=True,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_pattern(target_pattern)

        self.assertEqual(conflicts, [])

    def test_pattern_conflict_detection_ignores_different_weekday(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        base_pattern = create_schedule_pattern(
            organization=room.organization,
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            group=group,
            is_active=True,
            status=ScheduleStatus.DRAFT,
        )

        target_pattern = create_schedule_pattern(
            organization=base_pattern.organization,
            academic_year=base_pattern.academic_year,
            education_period=base_pattern.education_period,
            course=base_pattern.course,
            group_subject=base_pattern.group_subject,
            subject=base_pattern.subject,
            group=group,
            weekday=Weekday.TUESDAY,
            starts_at=base_pattern.starts_at,
            ends_at=base_pattern.ends_at,
            teacher=teacher,
            room=room,
            is_active=True,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_pattern(target_pattern)

        self.assertEqual(conflicts, [])
