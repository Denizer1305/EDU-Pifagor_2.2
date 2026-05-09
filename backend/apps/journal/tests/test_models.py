from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.journal.models import JournalGrade
from apps.journal.models.choices import GradeScale, GradeType, TopicProgressStatus
from apps.journal.tests.factories import (
    create_five_point_grade,
    create_journal_lesson,
    create_pass_fail_grade,
    create_student_user,
)


class JournalLessonModelTestCase(TestCase):
    def test_topic_returns_actual_topic_when_exists(self):
        lesson = create_journal_lesson(
            planned_topic="Плановая тема",
            actual_topic="Фактическая тема",
        )

        self.assertEqual(lesson.topic, "Фактическая тема")

    def test_topic_returns_planned_topic_when_actual_topic_is_empty(self):
        lesson = create_journal_lesson(
            planned_topic="Плановая тема",
            actual_topic="",
        )

        self.assertEqual(lesson.topic, "Плановая тема")


class JournalGradeModelTestCase(TestCase):
    def test_five_point_grade_display_value(self):
        grade = create_five_point_grade(score=5)

        self.assertEqual(grade.display_value, "5")

    def test_pass_grade_display_value(self):
        grade = create_pass_fail_grade(is_passed=True)

        self.assertIn("зач", grade.display_value.lower())

    def test_fail_grade_display_value(self):
        grade = create_pass_fail_grade(is_passed=False)

        self.assertIn("незач", grade.display_value.lower())

    def test_student_can_have_two_grades_for_one_lesson(self):
        lesson = create_journal_lesson()
        student = create_student_user()

        create_five_point_grade(
            lesson=lesson,
            student=student,
            score=5,
            grade_type=GradeType.CLASSWORK,
        )
        create_five_point_grade(
            lesson=lesson,
            student=student,
            score=4,
            grade_type=GradeType.TEST,
        )

        grades_count = JournalGrade.objects.filter(
            lesson=lesson,
            student=student,
        ).count()

        self.assertEqual(grades_count, 2)

    def test_five_point_grade_requires_score_five(self):
        grade = JournalGrade(
            lesson=create_journal_lesson(),
            student=create_student_user(),
            grade_type=GradeType.CLASSWORK,
            scale=GradeScale.FIVE_POINT,
            score_five=None,
            is_passed=None,
            weight=1,
        )

        with self.assertRaises(ValidationError):
            grade.full_clean()

    def test_pass_fail_grade_requires_is_passed(self):
        grade = JournalGrade(
            lesson=create_journal_lesson(),
            student=create_student_user(),
            grade_type=GradeType.CREDIT,
            scale=GradeScale.PASS_FAIL,
            score_five=None,
            is_passed=None,
            weight=1,
        )

        with self.assertRaises(ValidationError):
            grade.full_clean()


class TopicProgressModelTestCase(TestCase):
    def test_topic_progress_is_behind(self):
        from apps.journal.models import TopicProgress

        lesson = create_journal_lesson()
        course_lesson = lesson.course_lesson

        progress = TopicProgress.objects.create(
            course=lesson.course,
            group=lesson.group,
            lesson=course_lesson,
            journal_lesson=None,
            planned_date=lesson.date,
            actual_date=None,
            status=TopicProgressStatus.BEHIND,
            days_behind=3,
        )

        self.assertTrue(progress.is_behind)
