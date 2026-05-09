from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.users.constants import (
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_REJECTED,
    ROLE_STUDENT,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
)
from apps.users.tests.test_api_profile.api_profile_base import ProfileApiBaseTestCase


class StudentProfileApiTestCase(ProfileApiBaseTestCase):
    """API-тесты student onboarding и проверки студенческого профиля."""

    def test_student_onboarding_submits_request(self):
        self.student.is_email_verified = True
        self.student.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.student)
        url = reverse("users:student-onboarding")

        payload = {
            "requested_organization_id": self.organization.id,
            "requested_department_id": self.department.id,
            "requested_group_id": self.group.id,
            "submitted_group_code": "group-secret",
            "student_code": "ST-001",
            "notes": "Хочу привязаться к группе",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.student.refresh_from_db()

        self.assertEqual(
            self.student.student_profile.verification_status,
            VERIFICATION_STATUS_PENDING,
        )
        self.assertEqual(
            self.student.student_profile.requested_group_id,
            self.group.id,
        )

    def test_student_profile_review_approve(self):
        self.student.student_profile.requested_organization = self.organization
        self.student.student_profile.requested_department = self.department
        self.student.student_profile.requested_group = self.group
        self.student.student_profile.submitted_group_code = "group-secret"
        self.student.student_profile.verification_status = VERIFICATION_STATUS_PENDING
        self.student.student_profile.save()

        self.student.is_email_verified = True
        self.student.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "users:student-profile-review",
            args=[self.student.student_profile.id],
        )

        payload = {
            "verification_status": VERIFICATION_STATUS_APPROVED,
            "verification_comment": "Подтверждено куратором",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.student.refresh_from_db()

        self.assertEqual(
            self.student.student_profile.verification_status,
            VERIFICATION_STATUS_APPROVED,
        )
        self.assertEqual(
            self.student.onboarding_status,
            ONBOARDING_STATUS_ACTIVE,
        )
        self.assertTrue(
            self.student.user_roles.filter(role__code=ROLE_STUDENT).exists()
        )

    def test_student_profile_review_reject(self):
        self.student.student_profile.verification_status = VERIFICATION_STATUS_PENDING
        self.student.student_profile.save()

        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "users:student-profile-review",
            args=[self.student.student_profile.id],
        )

        payload = {
            "verification_status": VERIFICATION_STATUS_REJECTED,
            "verification_comment": "Неверный код группы",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.student.refresh_from_db()

        self.assertEqual(
            self.student.student_profile.verification_status,
            VERIFICATION_STATUS_REJECTED,
        )
        self.assertEqual(
            self.student.onboarding_status,
            ONBOARDING_STATUS_REJECTED,
        )
