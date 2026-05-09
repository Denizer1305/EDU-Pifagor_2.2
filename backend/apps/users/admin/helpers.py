from __future__ import annotations


def get_user_full_name_or_email(user) -> str:
    """Возвращает ФИО пользователя из профиля или email."""

    if user is None:
        return "—"

    profile = getattr(user, "profile", None)
    if profile:
        full_name = getattr(profile, "full_name", "")
        if full_name:
            return full_name

    return getattr(user, "email", "—")
