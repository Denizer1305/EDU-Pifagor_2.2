from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.users.constants import (
    ONBOARDING_STATUS_ACTIVE,
    ROLE_TEACHER,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
)
from apps.users.tests.test_api_profile.api_profile_base import ProfileApiBaseTestCase


class TeacherProfileApiTestCase(ProfileApiBaseTestCase):
    """API-тесты teacher onboarding и проверки профиля преподавателя."""

    def test_teacher_onboarding_submits_request(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("users:teacher-onboarding")

        payload = {
            "requested_organization_id": self.organization.id,
            "requested_department_id": self.department.id,
            "position": "Преподаватель информатики",
            "employee_code": "EMP-777",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.teacher.teacher_profile.refresh_from_db()
        self.assertEqual(
            self.teacher.teacher_profile.verification_status,
            VERIFICATION_STATUS_PENDING,
        )

    def test_teacher_profile_review_approve(self):
        self.teacher.teacher_profile.requested_organization = self.organization
        self.teacher.teacher_profile.requested_department = self.department
        self.teacher.teacher_profile.verification_status = VERIFICATION_STATUS_PENDING
        self.teacher.teacher_profile.save()

        self.teacher.is_email_verified = True
        self.teacher.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "users:teacher-profile-review",
            args=[self.teacher.teacher_profile.id],
        )

        payload = {
            "verification_status": VERIFICATION_STATUS_APPROVED,
            "verification_comment": "Подтвержден как преподаватель",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.teacher.teacher_profile.refresh_from_db()
        self.teacher.refresh_from_db()

        self.assertEqual(
            self.teacher.teacher_profile.verification_status,
            VERIFICATION_STATUS_APPROVED,
        )
        self.assertEqual(
            self.teacher.onboarding_status,
            ONBOARDING_STATUS_ACTIVE,
        )
        self.assertTrue(
            self.teacher.user_roles.filter(role__code=ROLE_TEACHER).exists()
        )
