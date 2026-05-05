from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.users.tests.test_api_auth.api_auth_base import (
    AuthApiBaseTestCase,
)

User = get_user_model()


class AuthRegistrationApiTestCase(AuthApiBaseTestCase):
    """API-тесты регистрации пользователей."""

    @patch("apps.users.views.auth.registration.send_verify_email_task.delay")
    def test_register_student_success(self, mock_send_verify_email):
        url = reverse("users:register")

        response = self.client.post(
            url,
            data={
                "registration_type": "student",
                "email": "student-api-register@example.com",
                "password": self.password,
                "password_repeat": self.password,
                "first_name": "Иван",
                "last_name": "Студентов",
                "patronymic": "Иванович",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "student-api-register@example.com")
        self.assertEqual(response.data["registration_type"], "student")

        user = User.objects.get(email="student-api-register@example.com")
        self.assertTrue(hasattr(user, "profile"))
        self.assertTrue(hasattr(user, "student_profile"))
        mock_send_verify_email.assert_called_once()

    @patch("apps.users.views.auth.registration.send_verify_email_task.delay")
    def test_register_parent_success(self, mock_send_verify_email):
        url = reverse("users:register")

        response = self.client.post(
            url,
            data={
                "registration_type": "parent",
                "email": "parent-api-register@example.com",
                "password": self.password,
                "password_repeat": self.password,
                "first_name": "Елена",
                "last_name": "Родительская",
                "work_place": "ООО Пифагор",
                "position": "Инженер",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "parent-api-register@example.com")
        self.assertEqual(response.data["registration_type"], "parent")

        user = User.objects.get(email="parent-api-register@example.com")
        self.assertTrue(hasattr(user, "parent_profile"))
        mock_send_verify_email.assert_called_once()

    @patch("apps.users.views.auth.registration.send_verify_email_task.delay")
    def test_register_teacher_success(self, mock_send_verify_email):
        organization, department = self.create_organization_stack()
        teacher_code = self.set_teacher_registration_code(organization)

        url = reverse("users:register")

        response = self.client.post(
            url,
            data={
                "registration_type": "teacher",
                "email": "teacher-api-register@example.com",
                "password": self.password,
                "password_repeat": self.password,
                "first_name": "Пётр",
                "last_name": "Преподавателев",
                "requested_organization_id": organization.id,
                "requested_department_id": department.id,
                "teacher_registration_code": teacher_code,
                "position": "Преподаватель информатики",
                "employee_code": "EMP-001",
                "education_info": "Высшее педагогическое",
                "experience_years": 5,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "teacher-api-register@example.com")
        self.assertEqual(response.data["registration_type"], "teacher")

        user = User.objects.get(email="teacher-api-register@example.com")
        self.assertTrue(hasattr(user, "teacher_profile"))
        self.assertEqual(
            user.teacher_profile.requested_organization_id, organization.id
        )
        self.assertEqual(user.teacher_profile.requested_department_id, department.id)
        mock_send_verify_email.assert_called_once()

    def test_register_invalid_registration_type_returns_400(self):
        url = reverse("users:register")

        response = self.client.post(
            url,
            data={
                "registration_type": "unknown_type",
                "email": "invalid-register@example.com",
                "password": self.password,
                "password_repeat": self.password,
                "first_name": "Иван",
                "last_name": "Иванов",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("registration_type", response.data)

    def test_register_password_mismatch_returns_400(self):
        url = reverse("users:register")

        response = self.client.post(
            url,
            data={
                "registration_type": "student",
                "email": "password-mismatch@example.com",
                "password": self.password,
                "password_repeat": "AnotherStrongPass123!",
                "first_name": "Иван",
                "last_name": "Иванов",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_repeat", response.data)
