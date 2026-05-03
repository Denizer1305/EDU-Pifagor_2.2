from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.users.constants import (
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_REJECTED,
    ROLE_TEACHER,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
)
from apps.users.services.role_services import user_has_role
from apps.users.services.teacher_services import (
    approve_teacher_profile,
    reject_teacher_profile,
    submit_teacher_verification_request,
)
from apps.users.tests.test_services.service_base import BaseUsersServiceTestCase


class TeacherServicesTestCase(BaseUsersServiceTestCase):
    def test_submit_teacher_verification_request(self):
        organization, department, _ = self.create_org_stack()
        user = self.create_user(
            "teacher-approve@example.com",
            registration_type="teacher",
            is_email_verified=True,
        )

        profile = submit_teacher_verification_request(
            teacher_profile=user.teacher_profile,
            requested_organization=organization,
            requested_department=department,
            position="Преподаватель информатики",
            employee_code="EMP-001",
        )

        self.assertEqual(profile.requested_organization, organization)
        self.assertEqual(
            profile.verification_status,
            VERIFICATION_STATUS_PENDING,
        )

    def test_approve_teacher_profile(self):
        reviewer = self.create_user(
            "reviewer-teacher@example.com",
            registration_type="teacher",
        )
        user = self.create_user(
            "teacher-approve@example.com",
            registration_type="teacher",
        )
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        profile = approve_teacher_profile(
            teacher_profile=user.teacher_profile,
            reviewer=reviewer,
            comment="Подтвержден",
        )

        user.refresh_from_db()

        self.assertEqual(
            profile.verification_status,
            VERIFICATION_STATUS_APPROVED,
        )
        self.assertEqual(
            user.onboarding_status,
            ONBOARDING_STATUS_ACTIVE,
        )
        self.assertTrue(user_has_role(user, ROLE_TEACHER))

    def test_reject_teacher_profile(self):
        reviewer = self.create_user(
            "reviewer-teacher-reject@example.com",
            registration_type="teacher",
        )
        user = self.create_user(
            "teacher-reject@example.com",
            registration_type="teacher",
        )

        profile = reject_teacher_profile(
            teacher_profile=user.teacher_profile,
            reviewer=reviewer,
            comment="Недостаточно данных",
        )

        user.refresh_from_db()

        self.assertEqual(
            profile.verification_status,
            VERIFICATION_STATUS_REJECTED,
        )
        self.assertEqual(
            user.onboarding_status,
            ONBOARDING_STATUS_REJECTED,
        )

    def test_approve_teacher_profile_without_verified_email_raises_validation_error(
        self,
    ):
        reviewer = self.create_user(
            "reviewer-teacher-email@example.com",
            registration_type="teacher",
        )
        user = self.create_user(
            "teacher-unverified@example.com",
            registration_type="teacher",
        )

        with self.assertRaises(ValidationError):
            approve_teacher_profile(
                teacher_profile=user.teacher_profile,
                reviewer=reviewer,
                comment="Подтвержден",
            )
