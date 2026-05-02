from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.journal.models import TopicProgress, TopicProgressStatus


def create_topic_progress(
    *,
    course_id: int,
    group_id: int,
    lesson_id: int,
    planned_date: date | None = None,
    actual_date: date | None = None,
    status: str = TopicProgressStatus.PLANNED,
    journal_lesson_id: int | None = None,
    comment: str = "",
) -> TopicProgress:
    """
    Создаёт запись о прогрессе прохождения темы КТП для группы.

    Уникальность course + group + lesson обеспечивается ограничением в БД,
    но для удобства проверяем заранее.
    """
    if TopicProgress.objects.filter(
        course_id=course_id, group_id=group_id, lesson_id=lesson_id
    ).exists():
        raise ValidationError(
            _("Запись о прогрессе для этой темы и группы уже существует.")
        )

    days_behind = _compute_days_behind(
        planned_date=planned_date, actual_date=actual_date, status=status
    )

    progress = TopicProgress(
        course_id=course_id,
        group_id=group_id,
        lesson_id=lesson_id,
        planned_date=planned_date,
        actual_date=actual_date,
        status=status,
        journal_lesson_id=journal_lesson_id,
        comment=comment,
        days_behind=days_behind,
    )
    progress.full_clean()
    progress.save()
    return progress


def update_topic_progress(
    *,
    progress: TopicProgress,
    status: str | None = None,
    actual_date: date | None = None,
    journal_lesson_id: int | None = None,
    comment: str | None = None,
) -> TopicProgress:
    """
    Обновляет запись о прогрессе темы.
    После обновления пересчитывает days_behind.
    """
    update_fields = ["updated_at"]

    if status is not None:
        progress.status = status
        update_fields.append("status")

    if actual_date is not None:
        progress.actual_date = actual_date
        update_fields.append("actual_date")

    if journal_lesson_id is not None:
        progress.journal_lesson_id = journal_lesson_id
        update_fields.append("journal_lesson_id")

    if comment is not None:
        progress.comment = comment
        update_fields.append("comment")

    # Пересчёт отставания
    progress.days_behind = _compute_days_behind(
        planned_date=progress.planned_date,
        actual_date=progress.actual_date,
        status=progress.status,
    )
    update_fields.append("days_behind")

    progress.full_clean()
    progress.save(update_fields=update_fields)
    return progress


def mark_topic_completed(
    *,
    progress: TopicProgress,
    actual_date: date | None = None,
    journal_lesson_id: int | None = None,
    comment: str = "",
) -> TopicProgress:
    """
    Помечает тему как пройденную.
    Если actual_date не передана — используется сегодняшняя дата.
    """
    return update_topic_progress(
        progress=progress,
        status=TopicProgressStatus.COMPLETED,
        actual_date=actual_date or date.today(),
        journal_lesson_id=journal_lesson_id,
        comment=comment or progress.comment,
    )


def recalculate_days_behind(*, progress: TopicProgress) -> TopicProgress:
    """
    Принудительно пересчитывает поле days_behind для записи.
    Используется в задачах Celery при пакетном пересчёте.
    """
    progress.days_behind = _compute_days_behind(
        planned_date=progress.planned_date,
        actual_date=progress.actual_date,
        status=progress.status,
    )
    progress.save(update_fields=["days_behind", "updated_at"])
    return progress


# ---------------------------------------------------------------------------
# Внутренние утилиты
# ---------------------------------------------------------------------------


def _compute_days_behind(
    *,
    planned_date: date | None,
    actual_date: date | None,
    status: str,
) -> int:
    """
    Вычисляет отставание в днях.

    Логика:
    - Если тема выполнена и есть обе даты: actual_date - planned_date.
    - Если тема ещё не выполнена и planned_date в прошлом: today - planned_date.
    - Иначе: 0.

    Положительное значение = отставание, отрицательное = опережение.
    """
    today = date.today()

    if status == TopicProgressStatus.COMPLETED:
        if planned_date and actual_date:
            return (actual_date - planned_date).days
        return 0

    if status in (TopicProgressStatus.PLANNED, TopicProgressStatus.BEHIND):
        if planned_date and planned_date < today:
            return (today - planned_date).days

    return 0
