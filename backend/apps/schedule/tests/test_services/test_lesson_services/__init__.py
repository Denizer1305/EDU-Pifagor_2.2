from __future__ import annotations

from unittest.mock import patch


def mute_journal_sync():
    """
    В локальном проекте post_save-сигнал schedule может синхронизировать занятие
    с журналом. Unit-тесты lesson_services не должны зависеть от journal_sync_services,
    поэтому синхронизацию глушим точечно.
    """
    return patch.multiple(
        "apps.schedule.signals",
        create_journal_lesson_from_schedule=lambda *args, **kwargs: None,
        sync_cancelled_lesson_to_journal=lambda *args, **kwargs: None,
        sync_rescheduled_lesson_to_journal=lambda *args, **kwargs: None,
    )
