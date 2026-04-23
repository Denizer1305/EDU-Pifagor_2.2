from __future__ import annotations

from django.db import transaction

from apps.users.constants import (
    REGISTRATION_TYPE_PARENT,
    REGISTRATION_TYPE_STUDENT,
    REGISTRATION_TYPE_TEACHER,
)
from apps.users.models import ParentProfile, Profile, StudentProfile, TeacherProfile


def get_or_create_base_profile(user) -> Profile:
    """
    Возвращает базовый профиль пользователя.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@transaction.atomic
def update_base_profile(
    user,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    patronymic: str | None = None,
    phone: str | None = None,
    birth_date=None,
    gender: str | None = None,
    about: str | None = None,
    city: str | None = None,
    timezone_value: str | None = None,
    social_link_max: str | None = None,
    social_link_vk: str | None = None,
) -> Profile:
    """
    Обновляет базовый профиль пользователя.
    """
    profile = get_or_create_base_profile(user)

    if first_name is not None:
        profile.first_name = first_name.strip()
    if last_name is not None:
        profile.last_name = last_name.strip()
    if patronymic is not None:
        profile.patronymic = patronymic.strip()
    if phone is not None:
        profile.phone = phone.strip()
    if birth_date is not None:
        profile.birth_date = birth_date
    if gender is not None:
        profile.gender = gender
    if about is not None:
        profile.about = about.strip()
    if city is not None:
        profile.city = city.strip()
    if timezone_value is not None:
        profile.timezone = timezone_value.strip()
    if social_link_max is not None:
        profile.social_link_max = social_link_max.strip()
    if social_link_vk is not None:
        profile.social_link_vk = social_link_vk.strip()

    profile.full_clean()
    profile.save()
    return profile


def ensure_role_profile(user):
    """
    Гарантирует существование role-profile по типу регистрации.
    """
    if user.registration_type == REGISTRATION_TYPE_STUDENT:
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        return profile

    if user.registration_type == REGISTRATION_TYPE_PARENT:
        profile, _ = ParentProfile.objects.get_or_create(user=user)
        return profile

    if user.registration_type == REGISTRATION_TYPE_TEACHER:
        profile, _ = TeacherProfile.objects.get_or_create(user=user)
        return profile

    return None
