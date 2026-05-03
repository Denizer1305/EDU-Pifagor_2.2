from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.constants import ROLE_STUDENT, ROLE_TEACHER
from apps.users.models import Role
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
)

User = get_user_model()


class UserApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.student_role, _ = Role.objects.get_or_create(
            code=ROLE_STUDENT,
            defaults={"name": "Студент", "is_active": True},
        )
        self.teacher_role, _ = Role.objects.get_or_create(
            code=ROLE_TEACHER,
            defaults={"name": "Преподаватель", "is_active": True},
        )

        self.admin = User.objects.create_superuser(
            email="admin-user@example.com",
            password="StrongPass123!",
        )
        admin_profile = get_or_create_base_profile(self.admin)
        admin_profile.first_name = "Админ"
        admin_profile.last_name = "Главный"
        admin_profile.full_clean()
        admin_profile.save()

        self.user = self.create_user(
            "regular-user@example.com", registration_type="student"
        )
        self.teacher = self.create_user(
            "teacher-user@example.com", registration_type="teacher"
        )

    def create_user(
        self,
        email: str,
        registration_type: str = "student",
        password: str = "StrongPass123!",
    ):
        user = User.objects.create_user(
            email=email,
            password=password,
            registration_type=registration_type,
        )
        profile = get_or_create_base_profile(user)
        profile.first_name = "Иван"
        profile.last_name = email.split("@")[0].capitalize()
        profile.full_clean()
        profile.save()
        ensure_role_profile(user)
        return user

    def test_current_user_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("users:current-user")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_user_list_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("users:user-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("users:user-detail", args=[self.user.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_role_list_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("users:role-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_role_list_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("users:role-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_profile_owner_can_get_own_profile(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse(
            "users:teacher-profile-detail", args=[self.teacher.teacher_profile.id]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.teacher.email)

    def test_current_user_requires_authentication(self):
        url = reverse("users:current-user")

        response = self.client.get(url)

        self.assertIn(
            response.status_code,
            {
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            },
        )

    def test_user_detail_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-detail", args=[self.teacher.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
