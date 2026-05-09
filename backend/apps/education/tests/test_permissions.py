from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.education.permissions import (
    IsAdminOnly,
    IsAdminOrReadOnly,
    IsTeacherAssignmentOwnerOrAdmin,
    IsTeacherOrAdminReadOnly,
)
from apps.education.tests.factories import (
    create_teacher_group_subject,
    create_teacher_user,
)
from apps.users.tests.factories import create_admin_user, create_user


class EducationPermissionsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_is_admin_only_allows_admin(self):
        admin_user = create_admin_user()
        request = self.factory.get("/fake-url/")
        request.user = admin_user

        permission = IsAdminOnly()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_is_admin_only_denies_regular_user(self):
        user = create_user(email="regular_edu@example.com", password="TestPass123!")
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsAdminOnly()
        self.assertFalse(permission.has_permission(request, view=None))

    def test_is_admin_or_read_only_allows_read(self):
        user = create_user(email="reader_edu@example.com", password="TestPass123!")
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsAdminOrReadOnly()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_is_admin_or_read_only_denies_write_for_regular_user(self):
        user = create_user(email="writer_edu@example.com", password="TestPass123!")
        request = self.factory.post("/fake-url/", {})
        request.user = user

        permission = IsAdminOrReadOnly()
        self.assertFalse(permission.has_permission(request, view=None))

    def test_is_teacher_or_admin_read_only_allows_teacher_read(self):
        teacher = create_teacher_user()
        request = self.factory.get("/fake-url/")
        request.user = teacher

        permission = IsTeacherOrAdminReadOnly()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_is_teacher_assignment_owner_or_admin_allows_owner(self):
        teacher = create_teacher_user(email="owner_edu_teacher@example.com")
        assignment = create_teacher_group_subject(teacher=teacher)

        request = self.factory.get("/fake-url/")
        request.user = teacher

        permission = IsTeacherAssignmentOwnerOrAdmin()
        self.assertTrue(
            permission.has_object_permission(request, view=None, obj=assignment)
        )

    def test_is_teacher_assignment_owner_or_admin_allows_admin(self):
        teacher = create_teacher_user(email="teacher_for_edu_admin@example.com")
        assignment = create_teacher_group_subject(teacher=teacher)

        admin_user = create_admin_user()
        request = self.factory.get("/fake-url/")
        request.user = admin_user

        permission = IsTeacherAssignmentOwnerOrAdmin()
        self.assertTrue(
            permission.has_object_permission(request, view=None, obj=assignment)
        )
