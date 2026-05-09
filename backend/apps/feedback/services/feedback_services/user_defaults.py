from __future__ import annotations

from apps.feedback.models.base import normalize_text


def _get_profile(user):
    """Возвращает общий профиль пользователя, если он есть."""

    if not user or not getattr(user, "is_authenticated", False):
        return None

    return getattr(user, "profile", None)


def _get_user_full_name(user) -> str:
    """Возвращает ФИО пользователя из профиля."""

    profile = _get_profile(user)
    if profile and getattr(profile, "full_name", ""):
        return profile.full_name

    if user and hasattr(user, "full_name") and user.full_name:
        return user.full_name

    return ""


def _get_user_phone(user) -> str:
    """Возвращает телефон пользователя из профиля."""

    profile = _get_profile(user)
    if profile and getattr(profile, "phone", ""):
        return profile.phone

    return ""


def _get_user_organization_name(user) -> str:
    """Возвращает название организации пользователя из student/teacher profile."""

    if not user or not getattr(user, "is_authenticated", False):
        return ""

    teacher_profile = getattr(user, "teacher_profile", None)
    if teacher_profile:
        requested_organization = getattr(
            teacher_profile,
            "requested_organization",
            None,
        )
        if requested_organization is not None:
            return requested_organization.short_name or requested_organization.name

    student_profile = getattr(user, "student_profile", None)
    if student_profile:
        requested_organization = getattr(
            student_profile,
            "requested_organization",
            None,
        )
        if requested_organization is not None:
            return requested_organization.short_name or requested_organization.name

    return ""


def _apply_authenticated_user_defaults(
    *,
    user,
    full_name: str,
    email: str,
    phone: str,
    organization_name: str,
) -> tuple[str, str, str, str]:
    """Подставляет контактные данные из профиля для авторизованного пользователя."""

    if user and getattr(user, "is_authenticated", False):
        full_name = full_name or _get_user_full_name(user)
        email = email or getattr(user, "email", "")
        phone = phone or _get_user_phone(user)
        organization_name = organization_name or _get_user_organization_name(user)

    return (
        normalize_text(full_name),
        normalize_text(email),
        normalize_text(phone),
        normalize_text(organization_name),
    )
