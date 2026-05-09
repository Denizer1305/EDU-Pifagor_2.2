from __future__ import annotations

from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import ConflictSeverity, ConflictStatus, ConflictType
from apps.schedule.models import ScheduleConflict, ScheduledLesson

from .common import create_conflict, get_lesson_overlap_queryset


def _clear_lesson_conflicts(lesson: ScheduledLesson) -> None:
    if lesson.pk:
        ScheduleConflict.objects.filter(
            lesson=lesson,
            status=ConflictStatus.OPEN,
        ).delete()


def _detect_teacher_conflicts(
    lesson: ScheduledLesson,
    overlapping_lessons,
) -> list[ScheduleConflict]:
    if not lesson.teacher_id:
        return []

    return [
        create_conflict(
            organization=lesson.organization,
            conflict_type=ConflictType.TEACHER_OVERLAP,
            severity=ConflictSeverity.ERROR,
            lesson=lesson,
            related_lesson=related_lesson,
            teacher=lesson.teacher,
            conflict_date=lesson.date,
            starts_at=lesson.starts_at,
            ends_at=lesson.ends_at,
            message=_("Преподаватель уже занят в это время."),
        )
        for related_lesson in overlapping_lessons.filter(teacher_id=lesson.teacher_id)
    ]


def _detect_room_conflicts(
    lesson: ScheduledLesson,
    overlapping_lessons,
) -> list[ScheduleConflict]:
    if not lesson.room_id:
        return []

    return [
        create_conflict(
            organization=lesson.organization,
            conflict_type=ConflictType.ROOM_OVERLAP,
            severity=ConflictSeverity.ERROR,
            lesson=lesson,
            related_lesson=related_lesson,
            room=lesson.room,
            conflict_date=lesson.date,
            starts_at=lesson.starts_at,
            ends_at=lesson.ends_at,
            message=_("Аудитория уже занята в это время."),
        )
        for related_lesson in overlapping_lessons.filter(room_id=lesson.room_id)
    ]


def _detect_group_conflicts(
    lesson: ScheduledLesson,
    overlapping_lessons,
) -> list[ScheduleConflict]:
    group_ids = set()

    if lesson.group_id:
        group_ids.add(lesson.group_id)

    group_ids.update(
        lesson.audiences.filter(group_id__isnull=False).values_list(
            "group_id",
            flat=True,
        )
    )

    conflicts: list[ScheduleConflict] = []

    for group_id in group_ids:
        related_lessons = overlapping_lessons.filter(
            Q(group_id=group_id) | Q(audiences__group_id=group_id)
        ).distinct()

        for related_lesson in related_lessons:
            conflicts.append(
                create_conflict(
                    organization=lesson.organization,
                    conflict_type=ConflictType.GROUP_OVERLAP,
                    severity=ConflictSeverity.ERROR,
                    lesson=lesson,
                    related_lesson=related_lesson,
                    group_id=group_id,
                    conflict_date=lesson.date,
                    starts_at=lesson.starts_at,
                    ends_at=lesson.ends_at,
                    message=_("Группа уже занята в это время."),
                )
            )

    return conflicts


def _detect_student_conflicts(
    lesson: ScheduledLesson,
    overlapping_lessons,
) -> list[ScheduleConflict]:
    student_ids = set(
        lesson.audiences.filter(student_id__isnull=False).values_list(
            "student_id",
            flat=True,
        )
    )

    conflicts: list[ScheduleConflict] = []

    for student_id in student_ids:
        related_lessons = overlapping_lessons.filter(
            audiences__student_id=student_id
        ).distinct()

        for related_lesson in related_lessons:
            conflicts.append(
                create_conflict(
                    organization=lesson.organization,
                    conflict_type=ConflictType.STUDENT_OVERLAP,
                    severity=ConflictSeverity.ERROR,
                    lesson=lesson,
                    related_lesson=related_lesson,
                    conflict_date=lesson.date,
                    starts_at=lesson.starts_at,
                    ends_at=lesson.ends_at,
                    message=_("Студент уже занят в это время."),
                )
            )

    return conflicts


def _detect_lesson_integrity_conflicts(
    lesson: ScheduledLesson,
) -> list[ScheduleConflict]:
    conflicts: list[ScheduleConflict] = []

    if lesson.room_id and not lesson.room.is_active:
        conflicts.append(
            create_conflict(
                organization=lesson.organization,
                conflict_type=ConflictType.INACTIVE_ROOM,
                severity=ConflictSeverity.WARNING,
                lesson=lesson,
                room=lesson.room,
                conflict_date=lesson.date,
                starts_at=lesson.starts_at,
                ends_at=lesson.ends_at,
                message=_("У занятия указана неактивная аудитория."),
            )
        )

    if (
        lesson.group_id
        and hasattr(lesson.group, "is_active")
        and not lesson.group.is_active
    ):
        conflicts.append(
            create_conflict(
                organization=lesson.organization,
                conflict_type=ConflictType.INACTIVE_GROUP,
                severity=ConflictSeverity.WARNING,
                lesson=lesson,
                group=lesson.group,
                conflict_date=lesson.date,
                starts_at=lesson.starts_at,
                ends_at=lesson.ends_at,
                message=_("У занятия указана неактивная группа."),
            )
        )

    if (
        lesson.course_lesson_id
        and lesson.course_id
        and lesson.course_lesson.course_id != lesson.course_id
    ):
        conflicts.append(
            create_conflict(
                organization=lesson.organization,
                conflict_type=ConflictType.COURSE_LESSON_MISMATCH,
                severity=ConflictSeverity.ERROR,
                lesson=lesson,
                conflict_date=lesson.date,
                starts_at=lesson.starts_at,
                ends_at=lesson.ends_at,
                message=_("Занятие курса не относится к выбранному курсу."),
            )
        )

    return conflicts


def detect_conflicts_for_lesson(
    lesson: ScheduledLesson,
    *,
    clear_existing: bool = True,
) -> list[ScheduleConflict]:
    if clear_existing:
        _clear_lesson_conflicts(lesson)

    overlapping_lessons = get_lesson_overlap_queryset(lesson)

    conflicts: list[ScheduleConflict] = []
    conflicts.extend(_detect_teacher_conflicts(lesson, overlapping_lessons))
    conflicts.extend(_detect_room_conflicts(lesson, overlapping_lessons))
    conflicts.extend(_detect_group_conflicts(lesson, overlapping_lessons))
    conflicts.extend(_detect_student_conflicts(lesson, overlapping_lessons))
    conflicts.extend(_detect_lesson_integrity_conflicts(lesson))

    return conflicts
