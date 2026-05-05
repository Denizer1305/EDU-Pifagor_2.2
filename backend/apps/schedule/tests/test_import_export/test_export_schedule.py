from __future__ import annotations

from datetime import date, time

from django.test import TestCase

from apps.schedule.services.export_services import (
    export_group_schedule,
    export_period_schedule,
    export_room_schedule,
    export_teacher_schedule,
)
from apps.schedule.tests.factories.course import create_course, create_user
from apps.schedule.tests.factories.lessons import create_scheduled_lesson
from apps.schedule.tests.factories.rooms import create_schedule_room


class ExportScheduleTestCase(TestCase):
    def _create_export_lesson(
        self,
        *,
        course=None,
        teacher=None,
        room=None,
        lesson_date=None,
        starts_at=None,
        ends_at=None,
    ):
        course = course or create_course()
        teacher = teacher or create_user()
        room = room or create_schedule_room(organization=course.organization)

        return create_scheduled_lesson(
            organization=course.organization,
            academic_year=course.academic_year,
            education_period=course.period,
            course=course,
            group_subject=course.group_subject,
            group=course.group_subject.group,
            subject=course.subject,
            teacher=teacher,
            room=room,
            date=lesson_date or date(2025, 9, 1),
            starts_at=starts_at or time(9, 0),
            ends_at=ends_at or time(10, 30),
        )

    def test_export_group_schedule_returns_group_lessons_inside_range(self):
        course = create_course()
        teacher = create_user()
        room = create_schedule_room(organization=course.organization)

        first_lesson = self._create_export_lesson(
            course=course,
            teacher=teacher,
            room=room,
            lesson_date=date(2025, 9, 1),
            starts_at=time(9, 0),
            ends_at=time(10, 30),
        )
        second_lesson = self._create_export_lesson(
            course=course,
            teacher=teacher,
            room=room,
            lesson_date=date(2025, 9, 2),
            starts_at=time(11, 0),
            ends_at=time(12, 30),
        )
        self._create_export_lesson(
            course=course,
            teacher=teacher,
            room=room,
            lesson_date=date(2025, 10, 1),
        )

        data = export_group_schedule(
            course.group_subject.group,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )

        self.assertEqual(
            [row["id"] for row in data],
            [first_lesson.id, second_lesson.id],
        )
        self.assertEqual(data[0]["date"], date(2025, 9, 1))
        self.assertEqual(data[0]["starts_at"], time(9, 0))
        self.assertEqual(data[0]["ends_at"], time(10, 30))
        self.assertEqual(data[0]["group"], str(course.group_subject.group))
        self.assertEqual(data[0]["subject"], str(course.subject))
        self.assertEqual(data[0]["teacher"], str(teacher))
        self.assertEqual(data[0]["room"], str(room))
        self.assertEqual(data[0]["course"], str(course))

    def test_export_teacher_schedule_filters_by_teacher(self):
        course = create_course()
        target_teacher = create_user()
        other_teacher = create_user()
        room = create_schedule_room(organization=course.organization)

        target_lesson = self._create_export_lesson(
            course=course,
            teacher=target_teacher,
            room=room,
        )
        self._create_export_lesson(
            course=course,
            teacher=other_teacher,
            room=room,
        )

        data = export_teacher_schedule(target_teacher)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], target_lesson.id)
        self.assertEqual(data[0]["teacher"], str(target_teacher))

    def test_export_room_schedule_filters_by_room(self):
        course = create_course()
        teacher = create_user()
        target_room = create_schedule_room(organization=course.organization)
        other_room = create_schedule_room(organization=course.organization)

        target_lesson = self._create_export_lesson(
            course=course,
            teacher=teacher,
            room=target_room,
        )
        self._create_export_lesson(
            course=course,
            teacher=teacher,
            room=other_room,
        )

        data = export_room_schedule(target_room)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], target_lesson.id)
        self.assertEqual(data[0]["room"], str(target_room))

    def test_export_period_schedule_filters_by_organization_and_period(self):
        course = create_course()
        another_course = create_course()

        period_lesson = self._create_export_lesson(
            course=course,
            lesson_date=date(2025, 9, 1),
        )
        self._create_export_lesson(
            course=another_course,
            lesson_date=date(2025, 9, 1),
        )

        data = export_period_schedule(
            organization_id=course.organization_id,
            education_period_id=course.period_id,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], period_lesson.id)
        self.assertEqual(data[0]["course"], str(course))

    def test_export_period_schedule_applies_date_range(self):
        course = create_course()

        included_lesson = self._create_export_lesson(
            course=course,
            lesson_date=date(2025, 9, 10),
        )
        self._create_export_lesson(
            course=course,
            lesson_date=date(2025, 10, 10),
        )

        data = export_period_schedule(
            organization_id=course.organization_id,
            education_period_id=course.period_id,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], included_lesson.id)
