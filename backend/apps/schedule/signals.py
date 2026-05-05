from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.schedule.constants import ScheduleStatus
from apps.schedule.models import ScheduledLesson
from apps.schedule.services.conflict_services import detect_conflicts_for_lesson
from apps.schedule.services.journal_sync_services import (
    create_journal_lesson_from_schedule,
    sync_cancelled_lesson_to_journal,
    sync_rescheduled_lesson_to_journal,
)

AUTO_DETECT_CONFLICTS_ON_SAVE = False
AUTO_SYNC_JOURNAL_ON_SAVE = True


@receiver(post_save, sender=ScheduledLesson)
def detect_schedule_lesson_conflicts_on_save(
    sender,
    instance: ScheduledLesson,
    created: bool,
    **kwargs,
) -> None:
    if not AUTO_DETECT_CONFLICTS_ON_SAVE:
        return

    if instance.is_locked:
        return

    detect_conflicts_for_lesson(instance)


@receiver(post_save, sender=ScheduledLesson)
def sync_schedule_lesson_to_journal_on_save(
    sender,
    instance: ScheduledLesson,
    created: bool,
    **kwargs,
) -> None:
    if not AUTO_SYNC_JOURNAL_ON_SAVE:
        return

    if instance.status == ScheduleStatus.PUBLISHED:
        create_journal_lesson_from_schedule(lesson=instance)
        return

    if instance.status == ScheduleStatus.CANCELLED:
        sync_cancelled_lesson_to_journal(lesson=instance)
        return

    if instance.status == ScheduleStatus.RESCHEDULED:
        sync_rescheduled_lesson_to_journal(lesson=instance)
