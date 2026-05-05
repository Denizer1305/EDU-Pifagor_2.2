from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.schedule.constants import ScheduleStatus
from apps.schedule.selectors import (
    get_lesson_by_id,
    get_lesson_queryset,
    get_lessons_for_course,
    get_lessons_for_date,
    get_lessons_for_group,
    get_lessons_for_organization,
    get_lessons_for_period,
    get_lessons_for_room,
    get_lessons_for_teacher,
    get_locked_lessons,
    get_published_lessons,
)
from apps.schedule.tests.factories import (
    create_group,
    create_organization,
    create_scheduled_lesson,
)

from . import ids


class LessonSelectorsTestCase(TestCase):
    def test_lesson_selectors_filter_lessons(self):
        organization = create_organization()
        group = create_group(organization=organization)
        lesson_date = date(2025, 9, 1)

        lesson = create_scheduled_lesson(
            organization=organization,
            group=group,
            date=lesson_date,
            status=ScheduleStatus.PUBLISHED,
            is_public=True,
            is_locked=True,
        )
        other_lesson = create_scheduled_lesson(
            organization=organization,
            group=group,
            date=date(2025, 10, 1),
            is_public=False,
            is_locked=False,
        )

        self.assertIn(lesson.id, ids(get_lesson_queryset()))
        self.assertEqual(get_lesson_by_id(lesson_id=lesson.id), lesson)

        self.assertIn(
            lesson.id,
            ids(get_lessons_for_organization(organization_id=organization.id)),
        )
        self.assertIn(
            lesson.id,
            ids(
                get_lessons_for_date(
                    organization_id=organization.id,
                    target_date=lesson_date,
                    public_only=True,
                )
            ),
        )
        self.assertNotIn(
            other_lesson.id,
            ids(
                get_lessons_for_date(
                    organization_id=organization.id,
                    target_date=lesson_date,
                    public_only=True,
                )
            ),
        )
        self.assertIn(
            lesson.id,
            ids(
                get_lessons_for_period(
                    organization_id=organization.id,
                    starts_on=date(2025, 9, 1),
                    ends_on=date(2025, 9, 30),
                    public_only=True,
                )
            ),
        )
        self.assertIn(
            lesson.id,
            ids(get_lessons_for_group(group_id=lesson.group_id)),
        )
        self.assertIn(
            lesson.id,
            ids(get_lessons_for_teacher(teacher_id=lesson.teacher_id)),
        )
        self.assertIn(
            lesson.id,
            ids(get_lessons_for_room(room_id=lesson.room_id)),
        )
        self.assertIn(
            lesson.id,
            ids(get_lessons_for_course(course_id=lesson.course_id)),
        )
        self.assertIn(
            lesson.id,
            ids(get_published_lessons(organization_id=organization.id)),
        )
        self.assertIn(
            lesson.id,
            ids(get_locked_lessons(organization_id=organization.id)),
        )
