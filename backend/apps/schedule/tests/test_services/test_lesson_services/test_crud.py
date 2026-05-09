from __future__ import annotations

from datetime import date, time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import AudienceType, Weekday
from apps.schedule.models import ScheduledLessonAudience
from apps.schedule.services.lesson_services.crud import (
    create_scheduled_lesson as service_create_scheduled_lesson,
)
from apps.schedule.services.lesson_services.crud import (
    update_scheduled_lesson,
)
from apps.schedule.tests.factories import (
    create_schedule_time_slot,
    create_scheduled_lesson,
)
from apps.schedule.tests.factories.course import (
    create_course,
    create_course_lesson,
    create_group,
)


class LessonCrudServicesTestCase(TestCase):
    def test_create_scheduled_lesson_creates_lesson_and_audiences(self):
        group = create_group()
        course = create_course(group=group, organization=group.organization)
        course_lesson = create_course_lesson(course=course)
        time_slot = create_schedule_time_slot(organization=group.organization)

        with patch(
            "apps.schedule.services.lesson_services.crud.detect_conflicts_for_lesson"
        ) as detect_conflicts:
            lesson = service_create_scheduled_lesson(
                organization=group.organization,
                academic_year=course.academic_year,
                education_period=course.period,
                date=date(2025, 9, 1),
                time_slot=time_slot,
                group=group,
                subject=course.subject,
                group_subject=course.group_subject,
                course=course,
                course_lesson=course_lesson,
                title="Созданное занятие",
                audiences=[
                    {
                        "audience_type": AudienceType.GROUP,
                        "group": group,
                    }
                ],
            )

        self.assertIsNotNone(lesson.pk)
        self.assertEqual(lesson.weekday, Weekday.MONDAY)
        self.assertEqual(lesson.starts_at, time_slot.starts_at)
        self.assertEqual(lesson.ends_at, time_slot.ends_at)

        self.assertEqual(lesson.audiences.count(), 1)
        self.assertEqual(lesson.audiences.first().group, group)

        detect_conflicts.assert_called_once_with(lesson)

    def test_create_scheduled_lesson_can_skip_conflict_validation(self):
        group = create_group()
        course = create_course(group=group, organization=group.organization)
        course_lesson = create_course_lesson(course=course)
        time_slot = create_schedule_time_slot(organization=group.organization)

        with patch(
            "apps.schedule.services.lesson_services.crud.detect_conflicts_for_lesson"
        ) as detect_conflicts:
            lesson = service_create_scheduled_lesson(
                organization=group.organization,
                academic_year=course.academic_year,
                education_period=course.period,
                date=date(2025, 9, 1),
                time_slot=time_slot,
                group=group,
                subject=course.subject,
                group_subject=course.group_subject,
                course=course,
                course_lesson=course_lesson,
                title="Без проверки конфликтов",
                validate_conflicts=False,
            )

        self.assertIsNotNone(lesson.pk)
        detect_conflicts.assert_not_called()

    def test_create_scheduled_lesson_validates_time_range(self):
        group = create_group()
        course = create_course(group=group, organization=group.organization)
        time_slot = create_schedule_time_slot(organization=group.organization)

        with self.assertRaises(ValidationError):
            service_create_scheduled_lesson(
                organization=group.organization,
                academic_year=course.academic_year,
                education_period=course.period,
                date=date(2025, 9, 1),
                time_slot=time_slot,
                starts_at=time(12, 0),
                ends_at=time(11, 0),
                group=group,
                subject=course.subject,
                group_subject=course.group_subject,
                course=course,
                validate_conflicts=False,
            )

    def test_update_scheduled_lesson_updates_fields_and_replaces_audiences(self):
        lesson = create_scheduled_lesson()
        new_group = create_group(
            organization=lesson.organization,
            academic_year=lesson.academic_year.name,
        )
        new_time_slot = create_schedule_time_slot(
            organization=lesson.organization,
            starts_at=time(11, 0),
            ends_at=time(12, 30),
            duration_minutes=90,
        )

        updated_lesson = update_scheduled_lesson(
            lesson,
            title="Обновлённое занятие",
            planned_topic="Обновлённая тема",
            time_slot=new_time_slot,
            starts_at=new_time_slot.starts_at,
            ends_at=new_time_slot.ends_at,
            audiences=[
                {
                    "audience_type": AudienceType.GROUP,
                    "group": new_group,
                }
            ],
            validate_conflicts=False,
        )

        updated_lesson.refresh_from_db()

        self.assertEqual(updated_lesson.title, "Обновлённое занятие")
        self.assertEqual(updated_lesson.planned_topic, "Обновлённая тема")
        self.assertEqual(updated_lesson.time_slot, new_time_slot)
        self.assertEqual(updated_lesson.starts_at, new_time_slot.starts_at)
        self.assertEqual(updated_lesson.ends_at, new_time_slot.ends_at)

        self.assertEqual(updated_lesson.audiences.count(), 1)
        self.assertEqual(updated_lesson.audiences.first().group, new_group)

    def test_update_scheduled_lesson_keeps_audiences_when_audiences_is_none(self):
        lesson = create_scheduled_lesson()
        ScheduledLessonAudience.objects.create(
            scheduled_lesson=lesson,
            audience_type=AudienceType.GROUP,
            group=lesson.group,
        )

        update_scheduled_lesson(
            lesson,
            title="Только заголовок",
            audiences=None,
            validate_conflicts=False,
        )

        lesson.refresh_from_db()

        self.assertEqual(lesson.title, "Только заголовок")
        self.assertEqual(lesson.audiences.count(), 1)
