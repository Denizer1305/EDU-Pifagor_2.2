from __future__ import annotations

from datetime import date, time
from unittest.mock import patch

from django.test import TestCase

from apps.schedule.constants import GenerationSource, Weekday
from apps.schedule.models import ScheduledLesson
from apps.schedule.services.generation_services import generate_lessons_from_patterns
from apps.schedule.tests.factories import (
    create_schedule_pattern,
    create_scheduled_lesson,
)

from . import COMPLETED_STATUS, create_schedule_generation_batch


class GenerateLessonsFromPatternsTestCase(TestCase):
    def test_generate_lessons_from_patterns_creates_lessons_for_matching_weekdays(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        result = generate_lessons_from_patterns(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 14),
            detect_conflicts=False,
        )

        result.refresh_from_db()

        lessons = ScheduledLesson.objects.filter(pattern=pattern).order_by("date")

        self.assertEqual(lessons.count(), 2)
        self.assertEqual(
            [lesson.date for lesson in lessons],
            [
                date(2025, 9, 1),
                date(2025, 9, 8),
            ],
        )

        first_lesson = lessons.first()

        self.assertEqual(first_lesson.organization, pattern.organization)
        self.assertEqual(first_lesson.academic_year, pattern.academic_year)
        self.assertEqual(first_lesson.education_period, pattern.education_period)
        self.assertEqual(first_lesson.weekday, Weekday.MONDAY)
        self.assertEqual(first_lesson.time_slot, pattern.time_slot)
        self.assertEqual(first_lesson.starts_at, pattern.starts_at)
        self.assertEqual(first_lesson.ends_at, pattern.ends_at)
        self.assertEqual(first_lesson.group, pattern.group)
        self.assertEqual(first_lesson.subject, pattern.subject)
        self.assertEqual(first_lesson.course, pattern.course)
        self.assertEqual(first_lesson.course_lesson, pattern.course_lesson)
        self.assertEqual(first_lesson.source_type, GenerationSource.PATTERNS)

        self.assertEqual(result.status, COMPLETED_STATUS)
        self.assertIsNotNone(result.started_at)
        self.assertIsNotNone(result.finished_at)
        self.assertEqual(result.lessons_created, 2)
        self.assertEqual(result.lessons_updated, 0)
        self.assertEqual(result.conflicts_count, 0)
        self.assertEqual(result.log, "")

    def test_generate_lessons_from_patterns_respects_pattern_start_and_end_dates(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 8),
            ends_on=date(2025, 9, 8),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        result = generate_lessons_from_patterns(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 15),
            detect_conflicts=False,
        )

        result.refresh_from_db()

        lessons = ScheduledLesson.objects.filter(pattern=pattern)

        self.assertEqual(lessons.count(), 1)
        self.assertEqual(lessons.first().date, date(2025, 9, 8))
        self.assertEqual(result.lessons_created, 1)

    def test_generate_lessons_from_patterns_ignores_inactive_patterns(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
            is_active=False,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        result = generate_lessons_from_patterns(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 14),
            detect_conflicts=False,
        )

        result.refresh_from_db()

        self.assertFalse(ScheduledLesson.objects.filter(pattern=pattern).exists())
        self.assertEqual(result.status, COMPLETED_STATUS)
        self.assertEqual(result.lessons_created, 0)
        self.assertEqual(result.lessons_updated, 0)

    def test_generate_lessons_from_patterns_counts_existing_lessons_as_updated(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
            is_active=True,
        )

        existing_lesson = create_scheduled_lesson(
            organization=pattern.organization,
            academic_year=pattern.academic_year,
            education_period=pattern.education_period,
            pattern=pattern,
            course=pattern.course,
            group_subject=pattern.group_subject,
            group=pattern.group,
            subject=pattern.subject,
            course_lesson=pattern.course_lesson,
            time_slot=pattern.time_slot,
            starts_at=pattern.starts_at,
            ends_at=pattern.ends_at,
            date=date(2025, 9, 1),
            weekday=Weekday.MONDAY,
        )

        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        result = generate_lessons_from_patterns(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 8),
            detect_conflicts=False,
        )

        result.refresh_from_db()

        lessons = ScheduledLesson.objects.filter(pattern=pattern).order_by("date")

        self.assertEqual(lessons.count(), 2)
        self.assertIn(existing_lesson, lessons)
        self.assertEqual(result.lessons_created, 1)
        self.assertEqual(result.lessons_updated, 1)

    def test_generate_lessons_from_patterns_runs_conflict_detection_for_created_lessons(
        self,
    ):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        with patch(
            "apps.schedule.services.generation_services.detect_conflicts_for_lesson",
            return_value=[object(), object()],
        ) as detect_conflicts_mock:
            result = generate_lessons_from_patterns(
                batch=batch,
                starts_on=date(2025, 9, 1),
                ends_on=date(2025, 9, 1),
                detect_conflicts=True,
            )

        result.refresh_from_db()

        self.assertEqual(detect_conflicts_mock.call_count, 1)
        self.assertEqual(result.lessons_created, 1)
        self.assertEqual(result.conflicts_count, 2)

    def test_generate_lessons_from_patterns_can_skip_conflict_detection(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        with patch(
            "apps.schedule.services.generation_services.detect_conflicts_for_lesson",
        ) as detect_conflicts_mock:
            result = generate_lessons_from_patterns(
                batch=batch,
                starts_on=date(2025, 9, 1),
                ends_on=date(2025, 9, 1),
                detect_conflicts=False,
            )

        result.refresh_from_db()

        detect_conflicts_mock.assert_not_called()
        self.assertEqual(result.lessons_created, 1)
        self.assertEqual(result.conflicts_count, 0)

    def test_generate_lessons_from_patterns_raises_error_without_period_or_dates(self):
        batch = create_schedule_generation_batch(
            dry_run=False,
            education_period=None,
        )

        with self.assertRaises(ValueError):
            generate_lessons_from_patterns(batch=batch)
