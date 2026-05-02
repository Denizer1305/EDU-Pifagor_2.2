from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.users.constants import (
    LINK_STATUS_APPROVED,
    ONBOARDING_STATUS_ACTIVE,
    ROLE_PARENT,
)
from apps.users.models import ParentStudent
from apps.users.tests.test_api_profile.api_profile_base import (
    ProfileApiBaseTestCase,
    relation_type_father,
    relation_type_mother,
)


class ParentProfileApiTestCase(ProfileApiBaseTestCase):
    """API-тесты заявок родитель-студент."""

    def test_parent_student_create_request(self):
        self.client.force_authenticate(user=self.parent)
        url = reverse("users:parent-student-link-request")

        payload = {
            "student_user_id": self.student.id,
            "relation_type": relation_type_mother(),
            "comment": "Мама ученика",
            "is_primary": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        link = ParentStudent.objects.get(
            parent=self.parent,
            student=self.student,
        )
        self.assertEqual(link.status, "pending")

    def test_parent_student_review_approve(self):
        link = ParentStudent.objects.create(
            parent=self.parent,
            student=self.student,
            relation_type=relation_type_father(),
            status="pending",
            requested_by=self.parent,
        )

        self.parent.is_email_verified = True
        self.parent.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "users:parent-student-link-review",
            args=[link.id],
        )

        payload = {
            "status": LINK_STATUS_APPROVED,
            "comment": "Связь подтверждена",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        link.refresh_from_db()
        self.parent.refresh_from_db()

        self.assertEqual(link.status, LINK_STATUS_APPROVED)
        self.assertEqual(
            self.parent.onboarding_status,
            ONBOARDING_STATUS_ACTIVE,
        )
        self.assertTrue(self.parent.user_roles.filter(role__code=ROLE_PARENT).exists())
