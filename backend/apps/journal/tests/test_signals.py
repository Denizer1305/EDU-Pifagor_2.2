from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from apps.journal.models.choices import AttendanceStatus, JournalLessonStatus
from apps.journal.tests.factories import (
    create_attendance_record,
    create_five_point_grade,
    create_journal_lesson,
)


class JournalSignalsTestCase(TestCase):
    @patch("apps.journal.signals.recalculate_journal_summaries_for_lesson_task.delay")
    @patch("apps.journal.signals.sync_topic_progress_for_lesson_task.delay")
    def test_journal_lesson_save_enqueues_tasks(
        self,
        sync_topic_progress_delay,
        recalculate_summaries_delay,
    ):
        with self.captureOnCommitCallbacks(execute=True):
            lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        sync_topic_progress_delay.assert_called_once_with(lesson_id=lesson.id)
        recalculate_summaries_delay.assert_called_once_with(lesson_id=lesson.id)

    @patch("apps.journal.signals.recalculate_group_journal_summary_task.delay")
    @patch("apps.journal.signals.recalculate_student_journal_summary_task.delay")
    def test_attendance_save_enqueues_summary_tasks(
        self,
        recalculate_student_delay,
        recalculate_group_delay,
    ):
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        with self.captureOnCommitCallbacks(execute=True):
            attendance = create_attendance_record(
                lesson=lesson,
                status=AttendanceStatus.PRESENT,
            )

        recalculate_student_delay.assert_called_once_with(
            course_id=lesson.course_id,
            group_id=lesson.group_id,
            student_id=attendance.student_id,
        )
        recalculate_group_delay.assert_called_once_with(
            course_id=lesson.course_id,
            group_id=lesson.group_id,
        )

    @patch("apps.journal.signals.recalculate_group_journal_summary_task.delay")
    @patch("apps.journal.signals.recalculate_student_journal_summary_task.delay")
    def test_grade_save_enqueues_summary_tasks(
        self,
        recalculate_student_delay,
        recalculate_group_delay,
    ):
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        with self.captureOnCommitCallbacks(execute=True):
            grade = create_five_point_grade(lesson=lesson, score=5)

        recalculate_student_delay.assert_called_once_with(
            course_id=lesson.course_id,
            group_id=lesson.group_id,
            student_id=grade.student_id,
        )
        recalculate_group_delay.assert_called_once_with(
            course_id=lesson.course_id,
            group_id=lesson.group_id,
        )
