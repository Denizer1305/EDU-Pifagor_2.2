from __future__ import annotations

from apps.organizations.models import TeacherSubject


def get_teacher_subjects_queryset(
    *,
    teacher_id: int | None = None,
    subject_id: int | None = None,
    is_primary: bool | None = None,
    is_active: bool | None = None,
):
    """Возвращает связи преподавателей с предметами."""

    queryset = TeacherSubject.objects.select_related(
        "teacher",
        "teacher__profile",
        "subject",
        "subject__category",
    ).all()

    if teacher_id is not None:
        queryset = queryset.filter(teacher_id=teacher_id)

    if subject_id is not None:
        queryset = queryset.filter(subject_id=subject_id)

    if is_primary is not None:
        queryset = queryset.filter(is_primary=is_primary)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.order_by(
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "subject__name",
    )


def get_active_teacher_subjects_queryset(
    *,
    teacher_id: int | None = None,
    subject_id: int | None = None,
):
    """Возвращает активные связи преподавателей с предметами."""

    return get_teacher_subjects_queryset(
        teacher_id=teacher_id,
        subject_id=subject_id,
        is_active=True,
    )
