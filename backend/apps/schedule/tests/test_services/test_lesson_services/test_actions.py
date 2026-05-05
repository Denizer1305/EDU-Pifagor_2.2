from __future__ import annotations

from datetime import date, time
from unittest.mock import patch

from django.test import TestCase

from apps.schedule.constants import ScheduleChangeType, ScheduleStatus, Weekday
from apps.schedule.services.lesson_services.actions import (
    cancel_lesson,
    change_room,
    lock_lesson,
    publish_lesson,
    replace_teacher,
    reschedule_lesson,
    unlock_lesson,
)
from apps.schedule.tests.factories import (
    create_schedule_room,
    create_schedule_time_slot,
    create_scheduled_lesson,
    create_user,
)

from . import mute_journal_sync


class LessonActionServicesTestCase(TestCase):
    def test_publish_lesson_sets_published_status_and_creates_change(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.DRAFT)
        user = create_user()

        with mute_journal_sync():
            result = publish_lesson(
                lesson,
                user=user,
                reason="Готово к публикации",
                comment="Публикуем",
            )

        result.refresh_from_db()

        self.assertEqual(result.status, ScheduleStatus.PUBLISHED)
        self.assertTrue(result.is_public)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.PUBLISH)
        self.assertEqual(change.changed_by, user)
        self.assertEqual(change.reason, "Готово к публикации")
        self.assertEqual(change.comment, "Публикуем")

    def test_cancel_lesson_sets_cancelled_status_and_stores_old_values(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.PLANNED)
        user = create_user()

        old_date = lesson.date
        old_time_slot = lesson.time_slot
        old_starts_at = lesson.starts_at
        old_ends_at = lesson.ends_at
        old_room = lesson.room
        old_teacher = lesson.teacher

        with mute_journal_sync():
            result = cancel_lesson(
                lesson,
                user=user,
                reason="Преподаватель отсутствует",
                comment="Отмена занятия",
            )

        result.refresh_from_db()

        self.assertEqual(result.status, ScheduleStatus.CANCELLED)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.CANCEL)
        self.assertEqual(change.changed_by, user)
        self.assertEqual(change.reason, "Преподаватель отсутствует")
        self.assertEqual(change.comment, "Отмена занятия")
        self.assertEqual(change.old_date, old_date)
        self.assertEqual(change.old_time_slot, old_time_slot)
        self.assertEqual(change.old_starts_at, old_starts_at)
        self.assertEqual(change.old_ends_at, old_ends_at)
        self.assertEqual(change.old_room, old_room)
        self.assertEqual(change.old_teacher, old_teacher)

    def test_reschedule_lesson_updates_date_time_status_and_creates_change(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.PLANNED)
        user = create_user()

        old_date = lesson.date
        old_time_slot = lesson.time_slot
        old_starts_at = lesson.starts_at
        old_ends_at = lesson.ends_at

        new_time_slot = create_schedule_time_slot(
            organization=lesson.organization,
            number=old_time_slot.number + 30,
            starts_at=time(12, 0),
            ends_at=time(13, 30),
        )

        with (
            mute_journal_sync(),
            patch(
                "apps.schedule.services.lesson_services.actions.detect_conflicts_for_lesson"
            ) as detect_conflicts,
        ):
            result = reschedule_lesson(
                lesson,
                new_date=date(2025, 9, 3),
                new_time_slot=new_time_slot,
                user=user,
                reason="Перенос",
                comment="Переносим на другой слот",
            )

        result.refresh_from_db()

        self.assertEqual(result.date, date(2025, 9, 3))
        self.assertEqual(result.weekday, Weekday.WEDNESDAY)
        self.assertEqual(result.time_slot, new_time_slot)
        self.assertEqual(result.starts_at, new_time_slot.starts_at)
        self.assertEqual(result.ends_at, new_time_slot.ends_at)
        self.assertEqual(result.status, ScheduleStatus.RESCHEDULED)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.RESCHEDULE)
        self.assertEqual(change.old_date, old_date)
        self.assertEqual(change.new_date, date(2025, 9, 3))
        self.assertEqual(change.old_time_slot, old_time_slot)
        self.assertEqual(change.new_time_slot, new_time_slot)
        self.assertEqual(change.old_starts_at, old_starts_at)
        self.assertEqual(change.new_starts_at, new_time_slot.starts_at)
        self.assertEqual(change.old_ends_at, old_ends_at)
        self.assertEqual(change.new_ends_at, new_time_slot.ends_at)

        detect_conflicts.assert_called_once_with(result)

    def test_reschedule_lesson_can_skip_conflict_validation(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.PLANNED)
        new_time_slot = create_schedule_time_slot(
            organization=lesson.organization,
            number=lesson.time_slot.number + 40,
            starts_at=time(14, 0),
            ends_at=time(15, 30),
        )

        with (
            mute_journal_sync(),
            patch(
                "apps.schedule.services.lesson_services.actions.detect_conflicts_for_lesson"
            ) as detect_conflicts,
        ):
            result = reschedule_lesson(
                lesson,
                new_date=date(2025, 9, 4),
                new_time_slot=new_time_slot,
                validate_conflicts=False,
            )

        result.refresh_from_db()

        self.assertEqual(result.date, date(2025, 9, 4))
        self.assertEqual(result.time_slot, new_time_slot)
        self.assertEqual(result.status, ScheduleStatus.RESCHEDULED)

        detect_conflicts.assert_not_called()

    def test_reschedule_lesson_raises_value_error_when_lesson_is_locked(self):
        lesson = create_scheduled_lesson(is_locked=True)

        with self.assertRaises(ValueError):
            reschedule_lesson(
                lesson,
                new_date=date(2025, 9, 5),
                validate_conflicts=False,
            )

    def test_replace_teacher_updates_teacher_status_and_creates_change(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.PLANNED)
        old_teacher = lesson.teacher
        new_teacher = create_user()
        user = create_user()

        with patch(
            "apps.schedule.services.lesson_services.actions.detect_conflicts_for_lesson"
        ) as detect_conflicts:
            result = replace_teacher(
                lesson,
                new_teacher=new_teacher,
                user=user,
                reason="Замена преподавателя",
                comment="Преподаватель заменён",
            )

        result.refresh_from_db()

        self.assertEqual(result.teacher, new_teacher)
        self.assertEqual(result.status, ScheduleStatus.REPLACED)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.REPLACE_TEACHER)
        self.assertEqual(change.old_teacher, old_teacher)
        self.assertEqual(change.new_teacher, new_teacher)
        self.assertEqual(change.changed_by, user)

        detect_conflicts.assert_called_once_with(result)

    def test_change_room_updates_room_status_and_creates_change(self):
        lesson = create_scheduled_lesson(status=ScheduleStatus.PLANNED)
        old_room = lesson.room
        new_room = create_schedule_room(organization=lesson.organization)
        user = create_user()

        with patch(
            "apps.schedule.services.lesson_services.actions.detect_conflicts_for_lesson"
        ) as detect_conflicts:
            result = change_room(
                lesson,
                new_room=new_room,
                user=user,
                reason="Смена аудитории",
                comment="Переезд в другую аудиторию",
            )

        result.refresh_from_db()

        self.assertEqual(result.room, new_room)
        self.assertEqual(result.status, ScheduleStatus.MOVED)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.CHANGE_ROOM)
        self.assertEqual(change.old_room, old_room)
        self.assertEqual(change.new_room, new_room)
        self.assertEqual(change.changed_by, user)

        detect_conflicts.assert_called_once_with(result)

    def test_lock_lesson_sets_locked_flag_and_creates_change(self):
        lesson = create_scheduled_lesson(is_locked=False)
        user = create_user()

        result = lock_lesson(
            lesson,
            user=user,
            reason="Фиксация расписания",
            comment="Блокируем",
        )

        result.refresh_from_db()

        self.assertTrue(result.is_locked)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.LOCK)
        self.assertEqual(change.changed_by, user)
        self.assertEqual(change.reason, "Фиксация расписания")
        self.assertEqual(change.comment, "Блокируем")

    def test_unlock_lesson_unsets_locked_flag_and_creates_change(self):
        lesson = create_scheduled_lesson(is_locked=True)
        user = create_user()

        result = unlock_lesson(
            lesson,
            user=user,
            reason="Можно редактировать",
            comment="Разблокируем",
        )

        result.refresh_from_db()

        self.assertFalse(result.is_locked)
        self.assertEqual(result.updated_by, user)

        change = result.changes.latest("created_at")
        self.assertEqual(change.change_type, ScheduleChangeType.UNLOCK)
        self.assertEqual(change.changed_by, user)
        self.assertEqual(change.reason, "Можно редактировать")
        self.assertEqual(change.comment, "Разблокируем")
