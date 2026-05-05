from __future__ import annotations

from datetime import date, time

from django.test import TestCase

from apps.schedule.constants import (
    ConflictStatus,
    ConflictType,
    ScheduleStatus,
    Weekday,
)
from apps.schedule.models import ScheduleConflict
from apps.schedule.services.conflict_services import detect_conflicts_for_lesson
from apps.schedule.tests.factories import (
    create_group,
    create_schedule_conflict,
    create_schedule_room,
    create_scheduled_lesson,
    create_user,
)


class LessonConflictIntegrationTestCase(TestCase):
    def test_overlapping_lessons_create_teacher_room_and_group_conflicts(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        base_lesson = create_scheduled_lesson(
            organization=room.organization,
            date=date(2025, 9, 8),
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            group=group,
            status=ScheduleStatus.DRAFT,
        )

        target_lesson = create_scheduled_lesson(
            organization=base_lesson.organization,
            academic_year=base_lesson.academic_year,
            education_period=base_lesson.education_period,
            course=base_lesson.course,
            group_subject=base_lesson.group_subject,
            subject=base_lesson.subject,
            group=group,
            date=base_lesson.date,
            weekday=base_lesson.weekday,
            time_slot=base_lesson.time_slot,
            starts_at=time(9, 30),
            ends_at=time(10, 0),
            teacher=teacher,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_lesson(target_lesson)
        conflict_types = {conflict.conflict_type for conflict in conflicts}

        self.assertIn(ConflictType.TEACHER_OVERLAP, conflict_types)
        self.assertIn(ConflictType.ROOM_OVERLAP, conflict_types)
        self.assertIn(ConflictType.GROUP_OVERLAP, conflict_types)

        self.assertEqual(
            ScheduleConflict.objects.filter(lesson=target_lesson).count(),
            3,
        )

    def test_adjacent_lessons_do_not_create_overlap_conflicts(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        base_lesson = create_scheduled_lesson(
            organization=room.organization,
            date=date(2025, 9, 8),
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 0),
            teacher=teacher,
            room=room,
            group=group,
            status=ScheduleStatus.DRAFT,
        )

        target_lesson = create_scheduled_lesson(
            organization=base_lesson.organization,
            academic_year=base_lesson.academic_year,
            education_period=base_lesson.education_period,
            course=base_lesson.course,
            group_subject=base_lesson.group_subject,
            subject=base_lesson.subject,
            group=group,
            date=base_lesson.date,
            weekday=base_lesson.weekday,
            starts_at=time(10, 0),
            ends_at=time(11, 0),
            teacher=teacher,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_lesson(target_lesson)

        self.assertEqual(conflicts, [])
        self.assertFalse(ScheduleConflict.objects.filter(lesson=target_lesson).exists())

    def test_cancelled_related_lesson_is_ignored(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        cancelled_lesson = create_scheduled_lesson(
            organization=room.organization,
            date=date(2025, 9, 9),
            weekday=Weekday.TUESDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            group=group,
            status=ScheduleStatus.CANCELLED,
        )

        target_lesson = create_scheduled_lesson(
            organization=cancelled_lesson.organization,
            academic_year=cancelled_lesson.academic_year,
            education_period=cancelled_lesson.education_period,
            course=cancelled_lesson.course,
            group_subject=cancelled_lesson.group_subject,
            subject=cancelled_lesson.subject,
            group=group,
            date=cancelled_lesson.date,
            weekday=cancelled_lesson.weekday,
            time_slot=cancelled_lesson.time_slot,
            starts_at=cancelled_lesson.starts_at,
            ends_at=cancelled_lesson.ends_at,
            teacher=teacher,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_lesson(target_lesson)

        self.assertEqual(conflicts, [])

    def test_inactive_room_creates_integrity_conflict(self):
        room = create_schedule_room(is_active=False)

        lesson = create_scheduled_lesson(
            organization=room.organization,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_lesson(lesson)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, ConflictType.INACTIVE_ROOM)
        self.assertEqual(conflicts[0].room, room)

    def test_existing_open_lesson_conflicts_are_cleared_before_detection(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.DRAFT)

        old_conflict = create_schedule_conflict(
            lesson=lesson,
            organization=lesson.organization,
            conflict_type=ConflictType.ROOM_OVERLAP,
            status=ConflictStatus.OPEN,
        )

        conflicts = detect_conflicts_for_lesson(lesson)

        self.assertEqual(conflicts, [])
        self.assertFalse(ScheduleConflict.objects.filter(pk=old_conflict.pk).exists())

    def test_ignored_lesson_conflicts_are_not_cleared(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.DRAFT)

        ignored_conflict = create_schedule_conflict(
            lesson=lesson,
            organization=lesson.organization,
            conflict_type=ConflictType.ROOM_OVERLAP,
            status=ConflictStatus.IGNORED,
        )

        conflicts = detect_conflicts_for_lesson(lesson)

        self.assertEqual(conflicts, [])
        self.assertTrue(
            ScheduleConflict.objects.filter(pk=ignored_conflict.pk).exists()
        )
