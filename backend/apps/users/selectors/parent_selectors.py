from __future__ import annotations

from apps.users.models import ParentProfile, ParentStudent


def get_parent_profiles_queryset():
    """Возвращает данные по заданным критериям."""
    return ParentProfile.objects.select_related("user", "user__profile")


def get_parent_student_links_queryset():
    """Возвращает данные по заданным критериям."""
    return ParentStudent.objects.select_related(
        "parent",
        "parent__profile",
        "student",
        "student__profile",
    )
