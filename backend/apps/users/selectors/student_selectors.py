from __future__ import annotations

from apps.users.models import StudentProfile


def get_student_profiles_queryset():
    """Возвращает данные по заданным критериям."""
    return StudentProfile.objects.select_related("user", "user__profile")
