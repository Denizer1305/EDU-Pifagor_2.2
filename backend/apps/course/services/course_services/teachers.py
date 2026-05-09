from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import Course, CourseTeacher


@transaction.atomic
def add_teacher_to_course(
    *,
    course: Course,
    teacher,
    role: str = CourseTeacher.RoleChoices.TEACHER,
    is_active: bool = True,
    can_edit: bool = True,
    can_manage_structure: bool = True,
    can_manage_assignments: bool = False,
    can_view_analytics: bool = True,
) -> CourseTeacher:
    """Добавляет преподавателя к курсу или обновляет существующую связь."""

    link, created = CourseTeacher.objects.get_or_create(
        course=course,
        teacher=teacher,
        defaults={
            "role": role,
            "is_active": is_active,
            "can_edit": can_edit,
            "can_manage_structure": can_manage_structure,
            "can_manage_assignments": can_manage_assignments,
            "can_view_analytics": can_view_analytics,
        },
    )

    if not created:
        link.role = role
        link.is_active = is_active
        link.can_edit = can_edit
        link.can_manage_structure = can_manage_structure
        link.can_manage_assignments = can_manage_assignments
        link.can_view_analytics = can_view_analytics
        link.full_clean()
        link.save(
            update_fields=[
                "role",
                "is_active",
                "can_edit",
                "can_manage_structure",
                "can_manage_assignments",
                "can_view_analytics",
                "updated_at",
            ]
        )

    return link


@transaction.atomic
def remove_teacher_from_course(*, course: Course, teacher) -> None:
    """Деактивирует преподавателя курса.

    Единственного активного владельца курса удалить нельзя.
    """

    link = CourseTeacher.objects.filter(course=course, teacher=teacher).first()
    if not link:
        return

    if link.role == CourseTeacher.RoleChoices.OWNER:
        owners_count = CourseTeacher.objects.filter(
            course=course,
            role=CourseTeacher.RoleChoices.OWNER,
            is_active=True,
        ).count()

        if owners_count <= 1:
            raise ValidationError(
                {"teacher": "Нельзя удалить единственного владельца курса."}
            )

    link.is_active = False
    link.full_clean()
    link.save(update_fields=["is_active", "updated_at"])
