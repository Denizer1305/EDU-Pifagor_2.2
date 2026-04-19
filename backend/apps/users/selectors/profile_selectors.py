from __future__ import annotations

from apps.users.models import Profile


def get_profiles_queryset():
    """Возвращает данные по заданным критериям."""
    return Profile.objects.select_related("user")


def get_profile_for_user(user):
    """Возвращает данные по заданным критериям."""
    return Profile.objects.select_related("user").get(user=user)
