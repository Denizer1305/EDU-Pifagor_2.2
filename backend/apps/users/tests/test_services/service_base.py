from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone

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
    """Возвращает значение типа связи 'мать' с учётом старых/новых enum."""

    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.MOTHER

    return ParentStudent.RelationType.MOTHER


def relation_type_father():
    """Возвращает значение типа связи 'отец' с учётом старых/новых enum."""

    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.FATHER

    return ParentStudent.RelationType.FATHER


def relation_type_guardian():
    """Возвращает значение типа связи 'опекун' с учётом старых/новых enum."""

    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.GUARDIAN

    return ParentStudent.RelationType.GUARDIAN


class BaseUsersServiceTestCase(TestCase):
    """Базовый класс для сервисных тестов users."""

    def setUp(self):
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

    def create_user(
        self,
        email: str,
        registration_type: str = "student",
    ):
        """Создаёт пользователя с базовым и ролевым профилем."""

        user = User.objects.create_user(
            email=email,
            password="StrongPass123!",
            registration_type=registration_type,
        )

        profile = get_or_create_base_profile(user)
        profile.first_name = "Иван"
        profile.last_name = email.split("@")[0].capitalize()
        profile.full_clean()
        profile.save()

        ensure_role_profile(user)
        return user

    def create_org_stack(self):
        """Создаёт организацию, подразделение и группу."""

        organization = create_organization(
            name="Сервисная организация",
            short_name="СервОрг",
        )
        department = create_department(
            organization=organization,
            name="Сервисное отделение",
            short_name="СервОтд",
        )
        group = create_group(
            organization=organization,
            department=department,
            name="Сервисная группа",
            code="SERV-01",
        )

        return organization, department, group

    def set_teacher_code(
        self,
        organization,
        code: str = "teacher-secret",
    ) -> str:
        """Устанавливает тестовый код регистрации преподавателя."""

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

    def set_group_code(
        self,
        group,
        code: str = "group-secret",
    ) -> str:
        """Устанавливает тестовый код присоединения к группе."""

        if hasattr(group, "join_code_hash"):
            group.join_code_hash = make_password(code)

        if hasattr(group, "join_code_is_active"):
            group.join_code_is_active = True

        if hasattr(group, "join_code_expires_at"):
            group.join_code_expires_at = timezone.now() + timedelta(days=1)

        group.save()
        return code
