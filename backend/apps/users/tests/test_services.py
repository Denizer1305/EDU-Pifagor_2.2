from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.constants import ROLE_TEACHER
from apps.users.models import Profile, UserRole
from apps.users.services.auth_services import change_user_password, register_user
from apps.users.services.profile_services import update_profile
from apps.users.services.role_services import assign_role, remove_role
from apps.users.tests.factories import create_profile, create_system_roles, create_user

User = get_user_model()


class AuthServicesTestCase(TestCase):
    def test_register_user_creates_user_and_profile(self):
        user = register_user(
            email="newuser@example.com",
            password="TestPass123!",
            first_name="Иван",
            last_name="Иванов",
            patronymic="Петрович",
            phone="+79990000001",
        )

        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("TestPass123!"))

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.first_name, "Иван")
        self.assertEqual(profile.last_name, "Иванов")
        self.assertEqual(profile.patronymic, "Петрович")
        self.assertEqual(profile.phone, "+79990000001")

    def test_change_user_password(self):
        user = create_user(email="pass@example.com", password="OldPass123!")
        change_user_password(user=user, new_password="NewPass123!")

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPass123!"))


class RoleServicesTestCase(TestCase):
    def test_assign_role(self):
        roles = create_system_roles()
        user = create_user(email="roleassign@example.com")

        user_role = assign_role(user=user, role=roles[ROLE_TEACHER])

        self.assertEqual(user_role.user, user)
        self.assertEqual(user_role.role.code, ROLE_TEACHER)
        self.assertTrue(UserRole.objects.filter(user=user, role=roles[ROLE_TEACHER]).exists())

    def test_remove_role(self):
        roles = create_system_roles()
        user = create_user(email="roleremove@example.com")

        assign_role(user=user, role=roles[ROLE_TEACHER])
        remove_role(user=user, role=roles[ROLE_TEACHER])

        self.assertFalse(UserRole.objects.filter(user=user, role=roles[ROLE_TEACHER]).exists())


class ProfileServicesTestCase(TestCase):
    def test_update_profile(self):
        profile = create_profile(
            first_name="Иван",
            last_name="Иванов",
            patronymic="Иванович",
        )

        update_profile(
            profile=profile,
            first_name="Петр",
            city="Москва",
            about="Обновленное описание",
        )

        profile.refresh_from_db()
        self.assertEqual(profile.first_name, "Петр")
        self.assertEqual(profile.city, "Москва")
        self.assertEqual(profile.about, "Обновленное описание")
