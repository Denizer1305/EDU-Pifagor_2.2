from __future__ import annotations

from apps.users.constants import (
    LINK_STATUS_APPROVED,
    LINK_STATUS_PENDING,
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_REJECTED,
    ROLE_PARENT,
)
from apps.users.services.parent_services import (
    approve_parent_student_link,
    create_parent_student_link_request,
    reject_parent_student_link,
)
from apps.users.services.role_services import user_has_role
from apps.users.tests.test_services.service_base import (
    BaseUsersServiceTestCase,
    relation_type_father,
    relation_type_guardian,
    relation_type_mother,
)


class ParentServicesTestCase(BaseUsersServiceTestCase):
    def test_create_parent_student_link_request(self):
        parent = self.create_user(
            "parent-service@example.com",
            registration_type="parent",
        )
        student = self.create_user(
            "student-service-link@example.com",
            registration_type="student",
        )

        link = create_parent_student_link_request(
            parent_user=parent,
            student_user=student,
            relation_type=relation_type_mother(),
            requested_by=parent,
            comment="Мама ученика",
        )

        self.assertEqual(link.status, LINK_STATUS_PENDING)

    def test_approve_parent_student_link(self):
        reviewer = self.create_user(
            "reviewer-parent@example.com",
            registration_type="teacher",
        )
        parent = self.create_user(
            "parent-approve@example.com",
            registration_type="parent",
            is_email_verified=True,
        )
        student = self.create_user(
            "student-approve-link@example.com",
            registration_type="student",
        )

        link = create_parent_student_link_request(
            parent_user=parent,
            student_user=student,
            relation_type=relation_type_father(),
            requested_by=parent,
        )

        approve_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment="Подтверждено",
        )

        link.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(link.status, LINK_STATUS_APPROVED)
        self.assertEqual(
            parent.onboarding_status,
            ONBOARDING_STATUS_ACTIVE,
        )
        self.assertTrue(user_has_role(parent, ROLE_PARENT))

    def test_reject_parent_student_link(self):
        reviewer = self.create_user(
            "reviewer-parent-reject@example.com",
            registration_type="teacher",
        )
        parent = self.create_user(
            "parent-reject@example.com",
            registration_type="parent",
        )
        student = self.create_user(
            "student-reject-link@example.com",
            registration_type="student",
        )

        link = create_parent_student_link_request(
            parent_user=parent,
            student_user=student,
            relation_type=relation_type_guardian(),
            requested_by=parent,
        )

        reject_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment="Связь не подтверждена",
        )

        link.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(link.status, "rejected")
        self.assertEqual(
            parent.onboarding_status,
            ONBOARDING_STATUS_REJECTED,
        )
