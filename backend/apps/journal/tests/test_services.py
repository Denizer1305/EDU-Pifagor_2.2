from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Model
from django.test import TestCase
from django.utils import timezone

from apps.journal.models import JournalSummary, TopicProgress
from apps.journal.models.choices import (
    AttendanceStatus,
    JournalLessonStatus,
    TopicProgressStatus,
)
from apps.journal.services.summary_services import recalculate_journal_summary
from apps.journal.services.topic_progress_services import (
    sync_topic_progress_for_course_group,
)
from apps.journal.tests.factories import (
    create_attendance_record,
    create_course_lesson,
    create_course_module,
    create_five_point_grade,
    create_group,
    create_journal_lesson,
    create_student_user,
)


def pk(obj: Model) -> int:
    """Возвращает pk модели как int для тестов и статического анализатора."""

    value: Any = obj.pk
    assert value is not None
    return int(value)


class JournalSummaryServiceTestCase(TestCase):
    def test_recalculate_student_journal_summary(self):
        student = create_student_user()
        first_lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)
        second_lesson = create_journal_lesson(
            course=first_lesson.course,
            group=first_lesson.group,
            teacher=first_lesson.teacher,
            status=JournalLessonStatus.CONDUCTED,
            lesson_number=2,
            date_value=first_lesson.date + timedelta(days=1),
        )

        create_attendance_record(
            lesson=first_lesson,
            student=student,
            status=AttendanceStatus.PRESENT,
        )
        create_attendance_record(
            lesson=second_lesson,
            student=student,
            status=AttendanceStatus.ABSENT,
        )

        create_five_point_grade(
            lesson=first_lesson,
            student=student,
            score=5,
        )
        create_five_point_grade(
            lesson=second_lesson,
            student=student,
            score=4,
        )

        course_id = pk(first_lesson.course)
        group_id = pk(first_lesson.group)
        student_id = pk(student)

        summary = recalculate_journal_summary(
            course_id=course_id,
            group_id=group_id,
            student_id=student_id,
        )

        self.assertEqual(summary.course_id, course_id)
        self.assertEqual(summary.group_id, group_id)
        self.assertEqual(summary.student_id, student_id)
        self.assertEqual(summary.total_lessons, 2)
        self.assertEqual(summary.attended_lessons, 1)
        self.assertEqual(summary.absent_lessons, 1)
        self.assertIsNotNone(summary.avg_score)

    def test_recalculate_group_journal_summary(self):
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        course_id = pk(lesson.course)
        group_id = pk(lesson.group)

        summary = recalculate_journal_summary(
            course_id=course_id,
            group_id=group_id,
            student_id=None,
        )

        self.assertEqual(summary.course_id, course_id)
        self.assertEqual(summary.group_id, group_id)
        self.assertIsNone(summary.student_id)

    def test_recalculate_journal_summary_updates_existing_row(self):
        student = create_student_user()
        lesson = create_journal_lesson(status=JournalLessonStatus.CONDUCTED)

        course_id = pk(lesson.course)
        group_id = pk(lesson.group)
        student_id = pk(student)

        first_summary = recalculate_journal_summary(
            course_id=course_id,
            group_id=group_id,
            student_id=student_id,
        )
        second_summary = recalculate_journal_summary(
            course_id=course_id,
            group_id=group_id,
            student_id=student_id,
        )

        self.assertEqual(first_summary.id, second_summary.id)
        self.assertEqual(
            JournalSummary.objects.filter(
                course=lesson.course,
                group=lesson.group,
                student=student,
            ).count(),
            1,
        )


class TopicProgressServiceTestCase(TestCase):
    def test_sync_topic_progress_for_course_group_creates_progress_items(self):
        group = create_group()
        first_lesson = create_journal_lesson(group=group)
        course = first_lesson.course
        module = create_course_module(course=course, order=2)

        second_course_lesson = create_course_lesson(
            course=course,
            module=module,
            order=2,
            title="Вторая тема",
        )

        progress_items = sync_topic_progress_for_course_group(
            course=course,
            group=group,
        )

        self.assertEqual(len(progress_items), 2)

        completed_progress = TopicProgress.objects.get(
            course=course,
            group=group,
            lesson=first_lesson.course_lesson,
        )
        planned_progress = TopicProgress.objects.get(
            course=course,
            group=group,
            lesson=second_course_lesson,
        )

        self.assertEqual(completed_progress.status, TopicProgressStatus.COMPLETED)
        self.assertIn(
            planned_progress.status,
            {
                TopicProgressStatus.PLANNED,
                TopicProgressStatus.BEHIND,
            },
        )

    def test_sync_topic_progress_marks_old_unconducted_topic_as_behind(self):
        group = create_group()
        course_lesson = create_course_lesson()
        old_date = timezone.localdate() - timedelta(days=3)

        course_lesson.available_from = timezone.make_aware(
            timezone.datetime.combine(old_date, timezone.datetime.min.time())
        )
        course_lesson.save(update_fields=("available_from", "updated_at"))

        progress_items = sync_topic_progress_for_course_group(
            course=course_lesson.course,
            group=group,
        )

        self.assertEqual(len(progress_items), 1)
        self.assertEqual(progress_items[0].status, TopicProgressStatus.BEHIND)
        self.assertEqual(progress_items[0].days_behind, 3)
