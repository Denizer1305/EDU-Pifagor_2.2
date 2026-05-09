from __future__ import annotations

from datetime import date, time

from django.test import TestCase

from apps.schedule.constants import ConflictType, ScheduleStatus, Weekday
from apps.schedule.services.conflict_services import detect_conflicts_for_period
from apps.schedule.tests.factories import (
    create_group,
    create_schedule_room,
    create_scheduled_lesson,
    create_user,
)


class PeriodConflictIntegrationTestCase(TestCase):
    def test_period_detection_checks_lessons_inside_date_range(self):
        teacher = create_user()
        room = create_schedule_room()
        group = create_group(organization=room.organization)

        base_lesson = create_scheduled_lesson(
            organization=room.organization,
            date=date(2025, 9, 10),
            weekday=Weekday.WEDNESDAY,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            teacher=teacher,
            room=room,
            group=group,
            status=ScheduleStatus.DRAFT,
        )

        create_scheduled_lesson(
            organization=base_lesson.organization,
            academic_year=base_lesson.academic_year,
            education_period=base_lesson.education_period,
            course=base_lesson.course,
            group_subject=base_lesson.group_subject,
            subject=base_lesson.subject,
            group=group,
            date=base_lesson.date,
            weekday=base_lesson.weekday,
            time_slot=base_lesson.time_slot,
            starts_at=time(9, 30),
            ends_at=time(10, 0),
            teacher=teacher,
            room=room,
            status=ScheduleStatus.DRAFT,
        )

        conflicts = detect_conflicts_for_period(
            organization=base_lesson.organization,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )

        conflict_types = {conflict.conflict_type for conflict in conflicts}

        self.assertIn(ConflictType.TEACHER_OVERLAP, conflict_types)
        self.assertIn(ConflictType.ROOM_OVERLAP, conflict_types)
        self.assertIn(ConflictType.GROUP_OVERLAP, conflict_types)

        self.assertTrue(
            all(
                date(2025, 9, 1) <= conflict.date <= date(2025, 9, 30)
                for conflict in conflicts
                if conflict.date is not None
            )
        )
