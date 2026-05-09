from __future__ import annotations

from datetime import date, time
from unittest.mock import patch

from django.test import TestCase

from apps.schedule.constants import BatchStatus
from apps.schedule.models import ScheduledLesson
from apps.schedule.services.import_services import (
    apply_import_batch,
    import_schedule_from_table,
    parse_uploaded_schedule,
)
from apps.schedule.tests.factories.course import create_course, create_user
from apps.schedule.tests.factories.lessons import create_schedule_time_slot
from apps.schedule.tests.factories.rooms import create_schedule_room

from . import batch_status, create_schedule_import_batch


class ApplyImportBatchTestCase(TestCase):
    def _valid_row_data(self, *, course=None, lesson_date=None):
        course = course or create_course()
        time_slot = create_schedule_time_slot(
            organization=course.organization,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
        )
        room = create_schedule_room(organization=course.organization)
        teacher = create_user()

        return {
            "date": lesson_date or date(2025, 9, 1),
            "starts_at": time(9, 0),
            "ends_at": time(10, 30),
            "time_slot": time_slot,
            "group": course.group_subject.group,
            "subject": course.subject,
            "teacher": teacher,
            "room": room,
            "course": course,
        }

    def test_apply_import_batch_creates_lessons_and_marks_success(self):
        course = create_course()
        batch = create_schedule_import_batch(course=course)
        parsed_rows = parse_uploaded_schedule(
            rows=[self._valid_row_data(course=course)]
        )

        with patch(
            "apps.schedule.services.import_services.detect_conflicts_for_lesson"
        ) as detect_conflicts_mock:
            result = apply_import_batch(
                batch=batch,
                rows=parsed_rows,
                validate_conflicts=True,
            )

        result.refresh_from_db()

        self.assertEqual(result.rows_total, 1)
        self.assertEqual(result.rows_success, 1)
        self.assertEqual(result.rows_failed, 0)
        self.assertEqual(result.status, batch_status("COMPLETED", "completed"))
        self.assertIsNotNone(result.started_at)
        self.assertIsNotNone(result.finished_at)
        self.assertEqual(result.log, "")

        lesson = ScheduledLesson.objects.get(course=course)

        self.assertEqual(lesson.organization, course.organization)
        self.assertEqual(lesson.academic_year, course.academic_year)
        self.assertEqual(lesson.education_period, course.period)
        self.assertEqual(lesson.date, date(2025, 9, 1))
        self.assertEqual(lesson.weekday, 1)
        self.assertEqual(lesson.group, course.group_subject.group)
        self.assertEqual(lesson.subject, course.subject)

        detect_conflicts_mock.assert_called_once_with(lesson)

    def test_apply_import_batch_records_invalid_rows_and_marks_partial(self):
        course = create_course()
        batch = create_schedule_import_batch(course=course)

        parsed_rows = parse_uploaded_schedule(
            rows=[
                self._valid_row_data(course=course),
                {
                    "date": "",
                    "starts_at": "",
                    "ends_at": "",
                },
            ]
        )

        result = apply_import_batch(
            batch=batch,
            rows=parsed_rows,
            validate_conflicts=False,
        )

        result.refresh_from_db()

        self.assertEqual(result.rows_total, 2)
        self.assertEqual(result.rows_success, 1)
        self.assertEqual(result.rows_failed, 1)
        self.assertEqual(result.status, BatchStatus.PARTIAL)
        self.assertIn("Строка 2", result.log)
        self.assertEqual(ScheduledLesson.objects.filter(course=course).count(), 1)

    def test_apply_import_batch_records_creation_errors_and_continues(self):
        course = create_course()
        batch = create_schedule_import_batch(course=course)

        parsed_rows = parse_uploaded_schedule(
            rows=[
                self._valid_row_data(course=course),
            ]
        )

        with patch(
            "apps.schedule.services.import_services._create_lesson_from_row",
            side_effect=ValueError("Сломанная строка импорта"),
        ) as create_lesson_mock:
            result = apply_import_batch(
                batch=batch,
                rows=parsed_rows,
                validate_conflicts=False,
            )

        result.refresh_from_db()

        self.assertEqual(result.rows_total, 1)
        self.assertEqual(result.rows_success, 0)
        self.assertEqual(result.rows_failed, 1)
        self.assertEqual(result.status, BatchStatus.PARTIAL)
        self.assertIn("Строка 1", result.log)
        self.assertIn("Сломанная строка импорта", result.log)

        self.assertFalse(ScheduledLesson.objects.filter(course=course).exists())
        create_lesson_mock.assert_called_once()

    def test_import_schedule_from_table_parses_rows_and_applies_batch(self):
        course = create_course()
        batch = create_schedule_import_batch(course=course)

        raw_rows = [
            self._valid_row_data(
                course=course,
                lesson_date=date(2025, 9, 2),
            )
        ]

        result = import_schedule_from_table(
            batch=batch,
            rows=raw_rows,
            validate_conflicts=False,
        )

        result.refresh_from_db()

        self.assertEqual(result.rows_total, 1)
        self.assertEqual(result.rows_success, 1)
        self.assertEqual(result.rows_failed, 0)
        self.assertEqual(result.status, batch_status("COMPLETED", "completed"))

        lesson = ScheduledLesson.objects.get(course=course)

        self.assertEqual(lesson.date, date(2025, 9, 2))
        self.assertEqual(lesson.starts_at, time(9, 0))
        self.assertEqual(lesson.ends_at, time(10, 30))
