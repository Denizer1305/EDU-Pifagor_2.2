from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.test import TestCase

from apps.schedule.constants import (
    AudienceType,
    LessonType,
    ScheduleSourceType,
    ScheduleStatus,
    Weekday,
)
from apps.schedule.models import SchedulePattern, SchedulePatternAudience
from apps.schedule.services.pattern_services import (
    copy_patterns_to_period,
    create_pattern,
    deactivate_pattern,
    update_pattern,
    validate_pattern,
)
from apps.schedule.tests.factories.course import (
    create_course,
    create_course_lesson,
    create_education_period,
    create_group,
)
from apps.schedule.tests.factories.lessons import create_schedule_time_slot
from apps.schedule.tests.factories.patterns import (
    create_schedule_pattern,
    create_schedule_pattern_audience,
)


def make_pattern_data(**overrides):
    course = overrides.pop("course", None) or create_course()
    course_lesson = overrides.pop("course_lesson", None) or create_course_lesson(
        course=course,
    )

    organization = overrides.pop("organization", None) or course.organization
    academic_year = overrides.pop("academic_year", None) or course.academic_year
    education_period = overrides.pop("education_period", None) or course.period
    group_subject = overrides.pop("group_subject", None) or course.group_subject
    subject = overrides.pop("subject", None) or course.subject

    group = overrides.pop("group", None)
    if group is None and group_subject is not None:
        group = group_subject.group

    time_slot = overrides.pop("time_slot", None) or create_schedule_time_slot(
        organization=organization,
    )

    starts_at = overrides.pop("starts_at", None) or time_slot.starts_at
    ends_at = overrides.pop("ends_at", None) or time_slot.ends_at

    starts_on = overrides.pop("starts_on", None)
    if starts_on is None and education_period is not None:
        starts_on = education_period.start_date
    if starts_on is None and academic_year is not None:
        starts_on = academic_year.start_date

    ends_on = overrides.pop("ends_on", None)
    if ends_on is None and education_period is not None:
        ends_on = education_period.end_date
    if ends_on is None and academic_year is not None:
        ends_on = academic_year.end_date

    data = {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "week_template": overrides.pop("week_template", None),
        "weekday": overrides.pop("weekday", Weekday.MONDAY),
        "time_slot": time_slot,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "group": group,
        "subject": subject,
        "teacher": overrides.pop("teacher", None),
        "room": overrides.pop("room", None),
        "group_subject": group_subject,
        "teacher_group_subject": overrides.pop("teacher_group_subject", None),
        "course": course,
        "course_lesson": course_lesson,
        "title": overrides.pop("title", "Тестовый шаблон расписания"),
        "lesson_type": overrides.pop("lesson_type", LessonType.LESSON),
        "source_type": overrides.pop("source_type", ScheduleSourceType.MANUAL),
        "status": overrides.pop("status", ScheduleStatus.DRAFT),
        "starts_on": starts_on,
        "ends_on": ends_on,
        "repeat_rule": overrides.pop("repeat_rule", ""),
        "priority": overrides.pop("priority", 100),
        "is_active": overrides.pop("is_active", True),
        "notes": overrides.pop("notes", ""),
    }
    data.update(overrides)
    return data


class PatternServicesTestCase(TestCase):
    def test_validate_pattern_runs_model_validation_and_returns_conflicts(self):
        pattern = create_schedule_pattern()

        with patch(
            "apps.schedule.services.pattern_services.detect_conflicts_for_pattern",
            return_value=["conflict"],
        ) as detect_conflicts_mock:
            result = validate_pattern(pattern)

        self.assertEqual(result, ["conflict"])
        detect_conflicts_mock.assert_called_once_with(pattern)

    def test_create_pattern_creates_pattern_and_audiences(self):
        data = make_pattern_data()
        group = data["group"]

        audiences = [
            {
                "audience_type": AudienceType.GROUP,
                "group": group,
                "notes": "Основная группа",
            }
        ]

        with patch(
            "apps.schedule.services.pattern_services.detect_conflicts_for_pattern",
            return_value=[],
        ) as detect_conflicts_mock:
            pattern = create_pattern(
                audiences=audiences,
                validate_conflicts=True,
                **data,
            )

        self.assertIsNotNone(pattern.pk)
        self.assertEqual(pattern.title, "Тестовый шаблон расписания")
        self.assertEqual(pattern.audiences.count(), 1)

        audience = pattern.audiences.get()
        self.assertEqual(audience.audience_type, AudienceType.GROUP)
        self.assertEqual(audience.group_id, group.id)
        self.assertEqual(audience.notes, "Основная группа")

        detect_conflicts_mock.assert_called_once_with(pattern)

    def test_create_pattern_can_skip_conflict_validation(self):
        data = make_pattern_data(title="Без проверки конфликтов")

        with patch(
            "apps.schedule.services.pattern_services.detect_conflicts_for_pattern",
        ) as detect_conflicts_mock:
            pattern = create_pattern(
                validate_conflicts=False,
                **data,
            )

        self.assertIsNotNone(pattern.pk)
        self.assertEqual(pattern.title, "Без проверки конфликтов")
        detect_conflicts_mock.assert_not_called()

    def test_update_pattern_updates_fields_and_replaces_audiences(self):
        pattern = create_schedule_pattern()
        create_schedule_pattern_audience(pattern=pattern)

        new_group = create_group(
            organization=pattern.organization,
            academic_year=pattern.academic_year.name,
        )

        with patch(
            "apps.schedule.services.pattern_services.detect_conflicts_for_pattern",
            return_value=[],
        ) as detect_conflicts_mock:
            updated_pattern = update_pattern(
                pattern,
                title="Обновлённый шаблон",
                weekday=Weekday.FRIDAY,
                audiences=[
                    {
                        "audience_type": AudienceType.GROUP,
                        "group": new_group,
                        "notes": "Новая группа",
                    }
                ],
            )

        updated_pattern.refresh_from_db()

        self.assertEqual(updated_pattern.title, "Обновлённый шаблон")
        self.assertEqual(updated_pattern.weekday, Weekday.FRIDAY)
        self.assertEqual(updated_pattern.audiences.count(), 1)

        audience = updated_pattern.audiences.get()
        self.assertEqual(audience.group_id, new_group.id)
        self.assertEqual(audience.notes, "Новая группа")

        detect_conflicts_mock.assert_called_once_with(updated_pattern)

    def test_update_pattern_can_clear_audiences(self):
        pattern = create_schedule_pattern()
        create_schedule_pattern_audience(pattern=pattern)

        with patch(
            "apps.schedule.services.pattern_services.detect_conflicts_for_pattern",
            return_value=[],
        ):
            updated_pattern = update_pattern(
                pattern,
                audiences=[],
                validate_conflicts=True,
            )

        self.assertEqual(updated_pattern.audiences.count(), 0)

    def test_deactivate_pattern_archives_pattern(self):
        pattern = create_schedule_pattern(
            status=ScheduleStatus.PUBLISHED,
            is_active=True,
        )

        deactivated_pattern = deactivate_pattern(pattern)
        deactivated_pattern.refresh_from_db()

        self.assertFalse(deactivated_pattern.is_active)
        self.assertEqual(deactivated_pattern.status, ScheduleStatus.ARCHIVED)

    def test_copy_patterns_to_period_copies_pattern_and_audiences(self):
        source_pattern = create_schedule_pattern(
            title="Исходный шаблон",
            status=ScheduleStatus.PUBLISHED,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 12, 31),
        )
        source_audience = create_schedule_pattern_audience(
            pattern=source_pattern,
            notes="Исходная аудитория",
        )

        new_period = create_education_period(
            academic_year=source_pattern.academic_year,
        )

        copied_patterns = copy_patterns_to_period(
            patterns=[source_pattern],
            education_period=new_period,
            starts_on=new_period.start_date,
            ends_on=new_period.end_date,
            copied_status=ScheduleStatus.DRAFT,
        )

        self.assertEqual(len(copied_patterns), 1)

        copied_pattern = copied_patterns[0]
        self.assertNotEqual(copied_pattern.pk, source_pattern.pk)
        self.assertEqual(copied_pattern.title, source_pattern.title)
        self.assertEqual(copied_pattern.education_period_id, new_period.id)
        self.assertEqual(copied_pattern.starts_on, new_period.start_date)
        self.assertEqual(copied_pattern.ends_on, new_period.end_date)
        self.assertEqual(copied_pattern.status, ScheduleStatus.DRAFT)
        self.assertTrue(copied_pattern.is_active)

        self.assertEqual(copied_pattern.audiences.count(), 1)

        copied_audience = copied_pattern.audiences.get()
        self.assertNotEqual(copied_audience.pk, source_audience.pk)
        self.assertEqual(copied_audience.audience_type, source_audience.audience_type)
        self.assertEqual(copied_audience.group_id, source_audience.group_id)
        self.assertEqual(copied_audience.notes, source_audience.notes)

        self.assertEqual(SchedulePattern.objects.count(), 2)
        self.assertEqual(SchedulePatternAudience.objects.count(), 2)
