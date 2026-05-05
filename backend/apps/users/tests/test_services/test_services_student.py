from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.users.constants import (
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_REJECTED,
    ROLE_STUDENT,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
)
from apps.users.services.role_services import user_has_role
from apps.users.services.student_services import (
    approve_student_profile,
    reject_student_profile,
    submit_student_group_request,
)
from apps.users.tests.test_services.service_base import BaseUsersServiceTestCase


class StudentServicesTestCase(BaseUsersServiceTestCase):
    def test_submit_student_group_request(self):
        organization, department, group = self.create_org_stack()
        group_code = self.set_group_code(group)

        user = self.create_user(
            "student-approve@example.com",
            registration_type="student",
            is_email_verified=True,
        )

        profile = submit_student_group_request(
            student_profile=user.student_profile,
            requested_organization=organization,
            requested_department=department,
            requested_group=group,
            submitted_group_code=group_code,
            student_code="ST-001",
        )

        self.assertEqual(profile.requested_group, group)
        self.assertEqual(
            profile.verification_status,
            VERIFICATION_STATUS_PENDING,
        )

    def test_approve_student_profile(self):
        reviewer = self.create_user(
            "reviewer-student@example.com",
            registration_type="teacher",
        )
        user = self.create_user(
            "student-approve@example.com",
            registration_type="student",
        )
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        profile = approve_student_profile(
            student_profile=user.student_profile,
            reviewer=reviewer,
            comment="Подтверждено",
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
        self.assertTrue(user_has_role(user, ROLE_STUDENT))

    def test_reject_student_profile(self):
        reviewer = self.create_user(
            "reviewer-student-reject@example.com",
            registration_type="teacher",
        )
        user = self.create_user(
            "student-reject@example.com",
            registration_type="student",
        )

        profile = reject_student_profile(
            student_profile=user.student_profile,
            reviewer=reviewer,
            comment="Код группы неверен",
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

    def test_approve_student_profile_without_verified_email_raises_validation_error(
        self,
    ):
        reviewer = self.create_user(
            "reviewer-student-email@example.com",
            registration_type="teacher",
        )
        user = self.create_user(
            "student-unverified@example.com",
            registration_type="student",
        )

        with self.assertRaises(ValidationError):
            approve_student_profile(
                student_profile=user.student_profile,
                reviewer=reviewer,
                comment="Подтверждено",
            )
