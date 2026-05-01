from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.users.constants import ONBOARDING_STATUS_DRAFT
from apps.users.services.profile_services import get_or_create_base_profile

User = get_user_model()


def _create_user_with_profile(
    *,
    email: str,
    password: str,
    reset_email: str,
    registration_type: str,
    first_name: str,
    last_name: str,
    patronymic: str,
    phone: str,
):
    """Создаёт пользователя и базовый профиль."""

    user = User.objects.create_user(
        email=email,
        password=password,
        reset_email=reset_email,
        registration_type=registration_type,
        onboarding_status=ONBOARDING_STATUS_DRAFT,
    )

    profile = get_or_create_base_profile(user)
    profile.first_name = first_name
    profile.last_name = last_name
    profile.patronymic = patronymic
    profile.phone = phone
    profile.full_clean()
    profile.save()

    return user
