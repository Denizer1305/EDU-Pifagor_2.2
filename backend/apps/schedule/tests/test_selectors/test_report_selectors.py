from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.schedule.selectors import (
    get_group_schedule_report,
    get_room_schedule_report,
    get_teacher_schedule_report,
)
from apps.schedule.tests.factories import (
    create_group,
    create_schedule_room,
    create_scheduled_lesson,
    create_user,
)


class ReportSelectorsTestCase(TestCase):
    def test_group_teacher_and_room_reports_return_lessons(self):
        group = create_group()
        teacher = create_user()
        room = create_schedule_room(organization=group.organization)

        lesson = create_scheduled_lesson(
            organization=group.organization,
            group=group,
            teacher=teacher,
            room=room,
            date=date(2025, 9, 1),
        )
        create_scheduled_lesson(
            organization=group.organization,
            group=group,
            teacher=teacher,
            room=room,
            date=date(2025, 10, 1),
        )

        group_report = get_group_schedule_report(
            group=group,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )
        teacher_report = get_teacher_schedule_report(
            teacher=teacher,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )
        room_report = get_room_schedule_report(
            room=room,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )

        self.assertEqual(group_report["group"], group.id)
        self.assertEqual(group_report["lessons_count"], 1)
        self.assertEqual(group_report["lessons"][0]["id"], lesson.id)

        self.assertEqual(teacher_report["teacher"], teacher.id)
        self.assertEqual(teacher_report["lessons_count"], 1)
        self.assertEqual(teacher_report["lessons"][0]["id"], lesson.id)

        self.assertEqual(room_report["room"], room.id)
        self.assertEqual(room_report["lessons_count"], 1)
        self.assertEqual(room_report["lessons"][0]["id"], lesson.id)
