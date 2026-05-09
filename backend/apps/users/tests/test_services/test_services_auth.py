from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.users.constants import VERIFICATION_STATUS_PENDING
from apps.users.services.auth_services import (
    authenticate_user,
    build_password_reset_token,
    build_verify_email_token,
    change_user_password,
    register_user,
    reset_password_by_token,
    verify_user_email_by_token,
)
from apps.users.tests.test_services.service_base import BaseUsersServiceTestCase


class AuthServicesTestCase(BaseUsersServiceTestCase):
    def test_register_student_user(self):
        user = register_user(
            email="student-register@example.com",
            password="StrongPass123!",
            password_repeat="StrongPass123!",
            registration_type="student",
            first_name="Иван",
            last_name="Студентов",
        )

        self.assertEqual(user.registration_type, "student")
        self.assertTrue(hasattr(user, "student_profile"))

    def test_register_teacher_user(self):
        organization, department, _ = self.create_org_stack()
        teacher_code = self.set_teacher_code(organization)

        user = register_user(
            email="teacher-register@example.com",
            password="StrongPass123!",
            password_repeat="StrongPass123!",
            registration_type="teacher",
            first_name="Петр",
            last_name="Преподавателев",
            requested_organization=organization,
            requested_department=department,
            teacher_registration_code=teacher_code,
            position="Преподаватель",
            employee_code="EMP-001",
        )

        self.assertEqual(
            user.teacher_profile.requested_organization,
            organization,
        )
        self.assertEqual(
            user.teacher_profile.verification_status,
            VERIFICATION_STATUS_PENDING,
        )

    def test_authenticate_user(self):
        user = self.create_user("auth@example.com")

        result = authenticate_user(
            email=user.email,
            password="StrongPass123!",
        )

        self.assertEqual(result.id, user.id)

    def test_verify_user_email_by_token(self):
        user = self.create_user("verify@example.com")
        token = build_verify_email_token(user)

        verify_user_email_by_token(token)
        user.refresh_from_db()

        self.assertTrue(user.is_email_verified)

    def test_reset_password_by_token(self):
        user = self.create_user("reset@example.com")
        token = build_password_reset_token(user)

        reset_password_by_token(
            token=token,
            password="NewStrongPass123!",
            password_repeat="NewStrongPass123!",
        )
        user.refresh_from_db()

        self.assertTrue(user.check_password("NewStrongPass123!"))

    def test_change_user_password(self):
        user = self.create_user("change@example.com")

        change_user_password(
            user=user,
            old_password="StrongPass123!",
            new_password="ChangedStrong123!",
            new_password_confirm="ChangedStrong123!",
        )
        user.refresh_from_db()

        self.assertTrue(user.check_password("ChangedStrong123!"))

    def test_authenticate_user_with_wrong_password_raises_validation_error(self):
        user = self.create_user("auth-wrong@example.com")

        with self.assertRaises(ValidationError):
            authenticate_user(
                email=user.email,
                password="WrongStrongPass123!",
            )

    def test_reset_password_by_token_password_mismatch_raises_validation_error(self):
        user = self.create_user("reset-mismatch-service@example.com")
        token = build_password_reset_token(user)

        with self.assertRaises(ValidationError):
            reset_password_by_token(
                token=token,
                password="NewStrongPass123!",
                password_repeat="AnotherStrongPass123!",
            )

    def test_change_user_password_wrong_old_password_raises_validation_error(self):
        user = self.create_user("change-wrong-service@example.com")

        with self.assertRaises(ValidationError):
            change_user_password(
                user=user,
                old_password="WrongStrongPass123!",
                new_password="ChangedStrong123!",
                new_password_confirm="ChangedStrong123!",
            )
