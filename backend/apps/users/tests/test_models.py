from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.models import ParentStudent, Profile, Role, UserRole
from apps.users.tests.factories import create_profile, create_system_roles, create_user

User = get_user_model()


def _relation_type_other():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.OTHER
    if hasattr(ParentStudent, "RelationType"):
        return ParentStudent.RelationType.OTHER
    return "other"


class UserModelTestCase(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="TEST@Example.com",
            password="TestPass123!",
        )

        self.assertEqual(user.email, "TEST@example.com")
        self.assertTrue(user.check_password("TestPass123!"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123!",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_reset_email_must_not_equal_email(self):
        user = User(
            email="user@example.com",
            reset_email="user@example.com",
        )
        with self.assertRaises(ValidationError):
            user.clean()

    def test_full_name_returns_profile_full_name(self):
        user = create_user(email="user1@example.com")
        create_profile(
            user=user,
            first_name="Иван",
            last_name="Иванов",
            patronymic="Петрович",
        )

        self.assertEqual(user.full_name, "Иванов Иван Петрович")


class ProfileModelTestCase(TestCase):
    def test_profile_full_name(self):
        profile = create_profile(
            first_name="Анна",
            last_name="Сидорова",
            patronymic="Викторовна",
        )
        self.assertEqual(profile.full_name, "Сидорова Анна Викторовна")

    def test_profile_short_name(self):
        profile = create_profile(
            first_name="Анна",
            last_name="Сидорова",
            patronymic="Викторовна",
        )
        self.assertEqual(profile.short_name, "Сидорова А. В.")

    def test_profile_requires_first_name(self):
        user = create_user(email="n1@example.com")
        profile = Profile(
            user=user,
            first_name="",
            last_name="Иванов",
        )
        with self.assertRaises(ValidationError):
            profile.clean()

    def test_profile_requires_last_name(self):
        user = create_user(email="n2@example.com")
        profile = Profile(
            user=user,
            first_name="Иван",
            last_name="",
        )
        with self.assertRaises(ValidationError):
            profile.clean()


class RoleModelTestCase(TestCase):
    def test_create_role(self):
        role = Role.objects.create(code="teacher", name="Преподаватель")
        self.assertEqual(role.code, "teacher")
        self.assertEqual(role.name, "Преподаватель")
        self.assertTrue(str(role))

    def test_user_role_is_unique(self):
        roles = create_system_roles()
        user = create_user(email="roleuser@example.com")

        UserRole.objects.create(user=user, role=roles["teacher"])

        with self.assertRaises(Exception):
            UserRole.objects.create(user=user, role=roles["teacher"])


class ParentStudentModelTestCase(TestCase):
    def test_parent_student_cannot_link_same_user(self):
        user = create_user(email="same@example.com", registration_type="parent")
        link = ParentStudent(
            parent=user,
            student=user,
            relation_type=_relation_type_other(),
        )

        with self.assertRaises(ValidationError):
            link.clean()
