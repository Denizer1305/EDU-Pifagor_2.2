from __future__ import annotations

from apps.users.models import TeacherProfile


def get_teacher_profiles_queryset():
    """Возвращает данные по заданным критериям."""
    return TeacherProfile.objects.select_related("user", "user__profile")


def get_public_teacher_profiles_queryset():
    """Возвращает данные по заданным критериям."""
    return get_teacher_profiles_queryset().filter(
        is_public=True,
        show_on_teachers_page=True,
    )
