from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.users.permissions import (
    CanManageUserRoles,
    IsParentProfileOwnerOrAdmin,
    IsTeacherProfileOwnerOrAdmin,
)
from apps.users.tests.factories import (
    create_admin_user,
    create_parent_user,
    create_teacher_user,
    create_user,
)


class PermissionsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_can_manage_user_roles_for_admin_role(self):
        user = create_admin_user()
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = CanManageUserRoles()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_can_manage_user_roles_for_regular_user_false(self):
        user = create_user(email="simple@example.com", password="TestPass123!")
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = CanManageUserRoles()
        self.assertFalse(permission.has_permission(request, view=None))

    def test_teacher_profile_owner_has_access(self):
        user, teacher_profile = create_teacher_user()
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsTeacherProfileOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(request, view=None, obj=teacher_profile))

    def test_teacher_profile_admin_has_access(self):
        admin = create_admin_user()
        _, teacher_profile = create_teacher_user(email="teacher2@example.com")

        request = self.factory.get("/fake-url/")
        request.user = admin

        permission = IsTeacherProfileOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(request, view=None, obj=teacher_profile))

    def test_teacher_profile_other_user_denied(self):
        other_user = create_user(email="other@example.com", password="TestPass123!")
        _, teacher_profile = create_teacher_user(email="teacher3@example.com")

        request = self.factory.get("/fake-url/")
        request.user = other_user

        permission = IsTeacherProfileOwnerOrAdmin()
        self.assertFalse(permission.has_object_permission(request, view=None, obj=teacher_profile))

    def test_parent_profile_owner_has_access(self):
        user, parent_profile = create_parent_user()
        request = self.factory.get("/fake-url/")
        request.user = user

        permission = IsParentProfileOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(request, view=None, obj=parent_profile))
