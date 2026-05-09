from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import (
    ConflictSeverity,
    ConflictStatus,
    ConflictType,
)
from apps.schedule.selectors import (
    get_conflict_by_id,
    get_conflict_queryset,
    get_conflicts_for_group,
    get_conflicts_for_lesson,
    get_conflicts_for_pattern,
    get_conflicts_for_period,
    get_conflicts_for_room,
    get_conflicts_for_teacher,
    get_open_conflicts,
)
from apps.schedule.tests.factories import (
    create_schedule_conflict,
    create_schedule_pattern,
    create_scheduled_lesson,
)

from . import ids


class ConflictSelectorsTestCase(TestCase):
    def test_conflict_selectors_filter_conflicts(self):
        lesson = create_scheduled_lesson()
        pattern = create_schedule_pattern(
            organization=lesson.organization,
            academic_year=lesson.academic_year,
            education_period=lesson.education_period,
            group=lesson.group,
            subject=lesson.subject,
            teacher=lesson.teacher,
            room=lesson.room,
            course=lesson.course,
            course_lesson=lesson.course_lesson,
        )

        conflict = create_schedule_conflict(
            organization=lesson.organization,
            lesson=lesson,
            pattern=pattern,
            teacher=lesson.teacher,
            room=lesson.room,
            group=lesson.group,
            date=lesson.date,
            starts_at=lesson.starts_at,
            ends_at=lesson.ends_at,
            conflict_type=ConflictType.TEACHER_OVERLAP,
            severity=ConflictSeverity.ERROR,
            status=ConflictStatus.OPEN,
        )
        resolved_conflict = create_schedule_conflict(
            organization=lesson.organization,
            lesson=lesson,
            teacher=lesson.teacher,
            room=lesson.room,
            group=lesson.group,
            date=lesson.date,
            status=ConflictStatus.RESOLVED,
        )

        self.assertIn(conflict.id, ids(get_conflict_queryset()))
        self.assertEqual(get_conflict_by_id(conflict_id=conflict.id), conflict)

        self.assertIn(
            conflict.id,
            ids(get_open_conflicts(organization_id=lesson.organization_id)),
        )
        self.assertNotIn(
            resolved_conflict.id,
            ids(get_open_conflicts(organization_id=lesson.organization_id)),
        )
        self.assertIn(
            conflict.id,
            ids(get_conflicts_for_lesson(lesson_id=lesson.id)),
        )
        self.assertIn(
            conflict.id,
            ids(get_conflicts_for_pattern(pattern_id=pattern.id)),
        )
        self.assertIn(
            conflict.id,
            ids(get_conflicts_for_teacher(teacher_id=lesson.teacher_id)),
        )
        self.assertIn(
            conflict.id,
            ids(get_conflicts_for_room(room_id=lesson.room_id)),
        )
        self.assertIn(
            conflict.id,
            ids(get_conflicts_for_group(group_id=lesson.group_id)),
        )
        self.assertIn(
            conflict.id,
            ids(
                get_conflicts_for_period(
                    organization_id=lesson.organization_id,
                    starts_on=lesson.date,
                    ends_on=lesson.date,
                    open_only=True,
                )
            ),
        )
        self.assertNotIn(
            resolved_conflict.id,
            ids(
                get_conflicts_for_period(
                    organization_id=lesson.organization_id,
                    starts_on=lesson.date,
                    ends_on=lesson.date,
                    open_only=True,
                )
            ),
        )
