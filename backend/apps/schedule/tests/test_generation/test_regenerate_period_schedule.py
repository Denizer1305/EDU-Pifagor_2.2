from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.schedule.constants import Weekday
from apps.schedule.models import ScheduledLesson
from apps.schedule.services.generation_services import regenerate_period_schedule
from apps.schedule.tests.factories import (
    create_schedule_pattern,
    create_scheduled_lesson,
)

from . import create_schedule_generation_batch


class RegeneratePeriodScheduleTestCase(TestCase):
    def test_regenerate_period_schedule_deletes_unlocked_existing_lessons(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=True,
        )

        unlocked_lesson = create_scheduled_lesson(
            organization=pattern.organization,
            academic_year=pattern.academic_year,
            education_period=pattern.education_period,
            course=pattern.course,
            group_subject=pattern.group_subject,
            group=pattern.group,
            subject=pattern.subject,
            course_lesson=pattern.course_lesson,
            date=date(2025, 9, 2),
            is_locked=False,
        )
        locked_lesson = create_scheduled_lesson(
            organization=pattern.organization,
            academic_year=pattern.academic_year,
            education_period=pattern.education_period,
            course=pattern.course,
            group_subject=pattern.group_subject,
            group=pattern.group,
            subject=pattern.subject,
            course_lesson=pattern.course_lesson,
            date=date(2025, 9, 3),
            is_locked=True,
        )

        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        result = regenerate_period_schedule(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 7),
            delete_unlocked_existing=True,
        )

        result.refresh_from_db()

        self.assertFalse(ScheduledLesson.objects.filter(pk=unlocked_lesson.pk).exists())
        self.assertTrue(ScheduledLesson.objects.filter(pk=locked_lesson.pk).exists())
        self.assertTrue(
            ScheduledLesson.objects.filter(
                pattern=pattern,
                date=date(2025, 9, 1),
            ).exists()
        )
        self.assertEqual(result.lessons_created, 1)

    def test_regenerate_period_schedule_keeps_existing_lessons_when_delete_disabled(
        self,
    ):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=True,
        )

        existing_lesson = create_scheduled_lesson(
            organization=pattern.organization,
            academic_year=pattern.academic_year,
            education_period=pattern.education_period,
            course=pattern.course,
            group_subject=pattern.group_subject,
            group=pattern.group,
            subject=pattern.subject,
            course_lesson=pattern.course_lesson,
            date=date(2025, 9, 2),
            is_locked=False,
        )

        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        regenerate_period_schedule(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 7),
            delete_unlocked_existing=False,
        )

        self.assertTrue(ScheduledLesson.objects.filter(pk=existing_lesson.pk).exists())
