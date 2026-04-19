from __future__ import annotations

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


def get_user_by_id(user_id: int) -> User:
    """Возвращает данные по заданным критериям."""
    return get_object_or_404(
        User.objects.select_related("profile"),
        pk=user_id,
    )


def get_user_by_email(email: str) -> User | None:
    """Возвращает данные по заданным критериям."""
    return User.objects.filter(email=email.strip().lower()).select_related("profile").first()


def get_users_queryset():
    """Возвращает данные по заданным критериям."""
    return User.objects.select_related("profile").prefetch_related("user_roles__role")
