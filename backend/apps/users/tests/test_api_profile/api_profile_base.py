from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_organization,
)
from apps.users.constants import (
    ROLE_PARENT,
    ROLE_STUDENT,
    ROLE_TEACHER,
)
from apps.users.models import ParentStudent, Role
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
)

User = get_user_model()


def relation_type_mother():
    """Возвращает тип связи 'мать' с учётом старого и нового enum."""

    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.MOTHER

    return ParentStudent.RelationType.MOTHER


def relation_type_father():
    """Возвращает тип связи 'отец' с учётом старого и нового enum."""

    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.FATHER

    return ParentStudent.RelationType.FATHER


class ProfileApiBaseTestCase(APITestCase):
    """Базовый класс для API-тестов профилей пользователей."""

    password = "StrongPass123!"

    def setUp(self):
        self._ensure_system_roles()

        self.organization = create_organization(
            name="Профильная организация",
            short_name="ПрофОрг",
        )
        self.department = create_department(
            organization=self.organization,
            name="Профильное отделение",
            short_name="ПрофОтд",
        )
        self.group = create_group(
            organization=self.organization,
            department=self.department,
            name="Профильная группа",
            code="PROF-01",
        )

        self.admin = User.objects.create_superuser(
            email="admin-profile@example.com",
            password=self.password,
        )
        self._fill_base_profile(
            user=self.admin,
            first_name="Админ",
            last_name="Системный",
        )

        self.student = self.create_user(
            "student-profile@example.com",
            registration_type="student",
        )
        self.teacher = self.create_user(
            "teacher-profile@example.com",
            registration_type="teacher",
        )
        self.parent = self.create_user(
            "parent-profile@example.com",
            registration_type="parent",
        )

        self.set_group_code(self.group)
        self.set_teacher_code(self.organization)

    def _ensure_system_roles(self) -> None:
        """Создаёт системные роли, необходимые для тестов."""

        Role.objects.get_or_create(
            code=ROLE_STUDENT,
            defaults={
                "name": "Студент",
                "is_active": True,
            },
        )
        Role.objects.get_or_create(
            code=ROLE_TEACHER,
            defaults={
                "name": "Преподаватель",
                "is_active": True,
            },
        )
        Role.objects.get_or_create(
            code=ROLE_PARENT,
            defaults={
                "name": "Родитель",
                "is_active": True,
            },
        )

    def _fill_base_profile(
        self,
        *,
        user,
        first_name: str,
        last_name: str,
    ):
        """Заполняет базовый профиль пользователя."""

        profile = get_or_create_base_profile(user)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.full_clean()
        profile.save()
        return profile

    def create_user(
        self,
        email: str,
        registration_type: str = "student",
        password: str = "StrongPass123!",
    ):
        """Создаёт пользователя с базовым и ролевым профилем."""

        user = User.objects.create_user(
            email=email,
            password=password,
            registration_type=registration_type,
        )

        self._fill_base_profile(
            user=user,
            first_name="Иван",
            last_name=email.split("@")[0].capitalize(),
        )

        ensure_role_profile(user)
        return user

    def set_group_code(
        self,
        group,
        code: str = "group-secret",
    ) -> str:
        """Активирует код присоединения к группе."""

        if hasattr(group, "join_code_hash"):
            group.join_code_hash = make_password(code)

        if hasattr(group, "join_code_is_active"):
            group.join_code_is_active = True

        if hasattr(group, "join_code_expires_at"):
            group.join_code_expires_at = timezone.now() + timedelta(days=1)

        group.save()
        return code

    def set_teacher_code(
        self,
        organization,
        code: str = "teacher-secret",
    ) -> str:
        """Активирует код регистрации преподавателя."""

        if hasattr(organization, "teacher_registration_code_hash"):
            organization.teacher_registration_code_hash = make_password(code)

        if hasattr(organization, "teacher_registration_code_is_active"):
            organization.teacher_registration_code_is_active = True

        if hasattr(organization, "teacher_registration_code_expires_at"):
            organization.teacher_registration_code_expires_at = (
                timezone.now() + timedelta(days=1)
            )

        organization.save()
        return code
