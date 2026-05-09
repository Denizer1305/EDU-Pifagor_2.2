from __future__ import annotations

from datetime import date, time

from django.test import TestCase

from apps.schedule.constants import (
    ConflictStatus,
    ConflictType,
    ScheduleStatus,
    Weekday,
)
from apps.schedule.services.conflict_services import (
    detect_conflicts_for_lesson,
    detect_conflicts_for_pattern,
    detect_conflicts_for_period,
    ignore_conflict,
    resolve_conflict,
)
from apps.schedule.tests.factories import (
    create_schedule_conflict,
    create_schedule_pattern,
    create_schedule_room,
    create_scheduled_lesson,
    create_user,
)


class LessonConflictServicesTestCase(TestCase):
    def test_detect_conflicts_for_lesson_creates_teacher_room_and_group_conflicts(self):
        teacher = create_user()
        room = create_schedule_room()

        base_lesson = create_scheduled_lesson(
            organization=room.organization,
            date=date(2025, 9, 1),
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        lesson = create_scheduled_lesson(
            organization=base_lesson.organization,
            academic_year=base_lesson.academic_year,
            education_period=base_lesson.education_period,
            date=base_lesson.date,
            weekday=base_lesson.weekday,
            time_slot=base_lesson.time_slot,
            starts_at=base_lesson.starts_at,
            ends_at=base_lesson.ends_at,
            teacher=teacher,
            room=room,
            group=base_lesson.group,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_lesson(lesson)

        conflict_types = {conflict.conflict_type for conflict in conflicts}

        self.assertIn(ConflictType.TEACHER_OVERLAP, conflict_types)
        self.assertIn(ConflictType.ROOM_OVERLAP, conflict_types)
        self.assertIn(ConflictType.GROUP_OVERLAP, conflict_types)

    def test_detect_conflicts_for_lesson_ignores_cancelled_lessons(self):
        cancelled_lesson = create_scheduled_lesson(
            date=date(2025, 9, 2),
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            status=ScheduleStatus.CANCELLED,
        )

        lesson = create_scheduled_lesson(
            organization=cancelled_lesson.organization,
            academic_year=cancelled_lesson.academic_year,
            education_period=cancelled_lesson.education_period,
            date=cancelled_lesson.date,
            weekday=cancelled_lesson.weekday,
            time_slot=cancelled_lesson.time_slot,
            starts_at=cancelled_lesson.starts_at,
            ends_at=cancelled_lesson.ends_at,
            teacher=cancelled_lesson.teacher,
            room=cancelled_lesson.room,
            group=cancelled_lesson.group,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_lesson(lesson)

        self.assertEqual(conflicts, [])

    def test_detect_conflicts_for_lesson_detects_inactive_room(self):
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

    def test_detect_conflicts_for_lesson_clears_existing_open_conflicts(self):
        lesson = create_scheduled_lesson()
        old_conflict = create_schedule_conflict(
            lesson=lesson,
            conflict_type=ConflictType.ROOM_OVERLAP,
            status=ConflictStatus.OPEN,
        )

        conflicts = detect_conflicts_for_lesson(lesson)

        self.assertFalse(
            old_conflict.__class__.objects.filter(pk=old_conflict.pk).exists()
        )
        self.assertEqual(conflicts, [])


class PatternConflictServicesTestCase(TestCase):
    def test_detect_conflicts_for_pattern_creates_teacher_room_and_group_conflicts(
        self,
    ):
        teacher = create_user()
        room = create_schedule_room()

        base_pattern = create_schedule_pattern(
            organization=room.organization,
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
        )

        pattern = create_schedule_pattern(
            organization=base_pattern.organization,
            academic_year=base_pattern.academic_year,
            education_period=base_pattern.education_period,
            weekday=base_pattern.weekday,
            time_slot=base_pattern.time_slot,
            starts_at=base_pattern.starts_at,
            ends_at=base_pattern.ends_at,
            teacher=teacher,
            room=room,
            group=base_pattern.group,
            status=ScheduleStatus.DRAFT,
            is_active=True,
        )

        conflicts = detect_conflicts_for_pattern(pattern)

        conflict_types = {conflict.conflict_type for conflict in conflicts}

        self.assertIn(ConflictType.TEACHER_OVERLAP, conflict_types)
        self.assertIn(ConflictType.ROOM_OVERLAP, conflict_types)
        self.assertIn(ConflictType.GROUP_OVERLAP, conflict_types)

    def test_detect_conflicts_for_pattern_ignores_different_weekday(self):
        base_pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
        )

        pattern = create_schedule_pattern(
            organization=base_pattern.organization,
            academic_year=base_pattern.academic_year,
            education_period=base_pattern.education_period,
            weekday=Weekday.TUESDAY,
            starts_at=base_pattern.starts_at,
            ends_at=base_pattern.ends_at,
            teacher=base_pattern.teacher,
            room=base_pattern.room,
            group=base_pattern.group,
            status=ScheduleStatus.DRAFT,
            is_active=True,
        )

        conflicts = detect_conflicts_for_pattern(pattern)

        self.assertEqual(conflicts, [])

    def test_detect_conflicts_for_pattern_ignores_non_overlapping_time(self):
        base_pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
        )

        pattern = create_schedule_pattern(
            organization=base_pattern.organization,
            academic_year=base_pattern.academic_year,
            education_period=base_pattern.education_period,
            weekday=base_pattern.weekday,
            starts_at=time(11, 0),
            ends_at=time(12, 30),
            teacher=base_pattern.teacher,
            room=base_pattern.room,
            group=base_pattern.group,
            status=ScheduleStatus.DRAFT,
            is_active=True,
        )

        conflicts = detect_conflicts_for_pattern(pattern)

        self.assertEqual(conflicts, [])


class PeriodConflictServicesTestCase(TestCase):
    def test_detect_conflicts_for_period_checks_lessons_inside_range(self):
        teacher = create_user()
        room = create_schedule_room()

        base_lesson = create_scheduled_lesson(
            organization=room.organization,
            date=date(2025, 9, 3),
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        lesson = create_scheduled_lesson(
            organization=base_lesson.organization,
            academic_year=base_lesson.academic_year,
            education_period=base_lesson.education_period,
            date=base_lesson.date,
            weekday=base_lesson.weekday,
            time_slot=base_lesson.time_slot,
            starts_at=base_lesson.starts_at,
            ends_at=base_lesson.ends_at,
            teacher=teacher,
            room=room,
            group=base_lesson.group,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_period(
            organization=lesson.organization,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
            lessons=[lesson],
        )

        conflict_types = {conflict.conflict_type for conflict in conflicts}

        self.assertIn(ConflictType.TEACHER_OVERLAP, conflict_types)
        self.assertIn(ConflictType.ROOM_OVERLAP, conflict_types)
        self.assertIn(ConflictType.GROUP_OVERLAP, conflict_types)


class ConflictResolutionServicesTestCase(TestCase):
    def test_resolve_conflict_marks_conflict_as_resolved(self):
        conflict = create_schedule_conflict(status=ConflictStatus.OPEN)

        resolved_conflict = resolve_conflict(
            conflict,
            notes="Исправлено вручную",
        )

        self.assertEqual(resolved_conflict.status, ConflictStatus.RESOLVED)
        self.assertEqual(resolved_conflict.notes, "Исправлено вручную")
        self.assertIsNotNone(resolved_conflict.resolved_at)

    def test_ignore_conflict_marks_conflict_as_ignored(self):
        conflict = create_schedule_conflict(status=ConflictStatus.OPEN)

        ignored_conflict = ignore_conflict(
            conflict,
            notes="Допустимый конфликт",
        )

        self.assertEqual(ignored_conflict.status, ConflictStatus.IGNORED)
        self.assertEqual(ignored_conflict.notes, "Допустимый конфликт")
        self.assertIsNone(ignored_conflict.resolved_at)
