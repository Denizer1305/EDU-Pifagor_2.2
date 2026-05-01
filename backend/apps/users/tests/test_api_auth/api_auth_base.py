from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.organizations.tests.factories import (
    create_department,
    create_organization,
)
from apps.users.services.profile_services import get_or_create_base_profile

User = get_user_model()


class AuthApiBaseTestCase(APITestCase):
    """Базовый класс для API-тестов авторизации."""

    password = "StrongPass123!"

    def create_user(
        self,
        *,
        email: str = "auth-user@example.com",
        password: str = "StrongPass123!",
        registration_type: str = "student",
        is_active: bool = True,
        onboarding_status: str | None = None,
        is_email_verified: bool = False,
    ):
        """Создаёт пользователя для API-тестов auth."""

        user = User.objects.create_user(
            email=email,
            password=password,
            registration_type=registration_type,
            is_active=is_active,
            is_email_verified=is_email_verified,
        )

        if onboarding_status is not None:
            user.onboarding_status = onboarding_status
            user.save(update_fields=("onboarding_status", "updated_at"))

        profile = get_or_create_base_profile(user)
        profile.first_name = "Иван"
        profile.last_name = "Тестовый"
        profile.full_clean()
        profile.save()

        return user

    def create_organization_stack(self):
        """Создаёт организацию и подразделение для регистрации преподавателя."""

        organization = create_organization(
            name="Auth API организация",
            short_name="AuthOrg",
        )
        department = create_department(
            organization=organization,
            name="Auth API отделение",
            short_name="AuthDep",
        )
        return organization, department

    def set_teacher_registration_code(
        self,
        organization,
        raw_code: str = "teacher-secret",
    ) -> str:
        """Активирует код регистрации преподавателя."""

        if hasattr(organization, "teacher_registration_code_hash"):
            organization.teacher_registration_code_hash = make_password(raw_code)

        if hasattr(organization, "teacher_registration_code_is_active"):
            organization.teacher_registration_code_is_active = True

        if hasattr(organization, "teacher_registration_code_expires_at"):
            organization.teacher_registration_code_expires_at = (
                timezone.now() + timedelta(days=1)
            )

        organization.save()
        return raw_code
