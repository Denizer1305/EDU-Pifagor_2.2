from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.organizations.permissions import (
    IsAdminOnly,
    IsAdminOrReadOnly,
    IsTeacherOrAdminReadOnly,
    IsTeacherOwnerOrAdmin,
)
from apps.organizations.tests.factories import (
    create_teacher_organization,
    create_teacher_subject,
    create_teacher_user,
)
from apps.users.tests.factories import create_admin_user, create_user


class OrganizationsPermissionsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_is_admin_only_allows_admin(self):
        admin_user = create_admin_user()
        request = self.factory.get("/fake-url/")
        request.user = admin_user

        permission = IsAdminOnly()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_is_admin_only_denies_regular_user(self):
        user = create_user(email="regular_perm@example.com", password="TestPass123!")
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsAdminOnly()
        self.assertFalse(permission.has_permission(request, view=None))

    def test_is_admin_or_read_only_allows_read_for_authenticated_user(self):
        user = create_user(email="reader@example.com", password="TestPass123!")
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsAdminOrReadOnly()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_is_admin_or_read_only_denies_write_for_regular_user(self):
        user = create_user(email="writer@example.com", password="TestPass123!")
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

    def test_is_teacher_or_admin_read_only_denies_regular_user_read(self):
        user = create_user(email="simple_read@example.com", password="TestPass123!")
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsTeacherOrAdminReadOnly()
        self.assertFalse(permission.has_permission(request, view=None))

    def test_is_teacher_owner_or_admin_allows_teacher_owner(self):
        teacher = create_teacher_user(email="owner_teacher@example.com")
        link = create_teacher_subject(teacher=teacher)

        request = self.factory.get("/fake-url/")
        request.user = teacher

        permission = IsTeacherOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(request, view=None, obj=link))

    def test_is_teacher_owner_or_admin_allows_admin(self):
        teacher = create_teacher_user(email="teacher_for_admin@example.com")
        link = create_teacher_organization(teacher=teacher)

        admin_user = create_admin_user()
        request = self.factory.get("/fake-url/")
        request.user = admin_user

        permission = IsTeacherOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(request, view=None, obj=link))

    def test_is_teacher_owner_or_admin_denies_other_teacher(self):
        owner_teacher = create_teacher_user(email="owner_teacher_2@example.com")
        other_teacher = create_teacher_user(email="other_teacher_2@example.com")
        link = create_teacher_subject(teacher=owner_teacher)

        request = self.factory.get("/fake-url/")
        request.user = other_teacher

        permission = IsTeacherOwnerOrAdmin()
        self.assertFalse(permission.has_object_permission(request, view=None, obj=link))
