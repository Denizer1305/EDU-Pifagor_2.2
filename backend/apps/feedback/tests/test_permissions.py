from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.feedback.permissions import (
    IsAdminOrSuperuser,
    IsFeedbackOwnerOrAdmin,
)
from apps.feedback.tests.factories import (
    create_feedback_admin_user,
    create_feedback_request,
    create_feedback_user,
)


class FeedbackPermissionsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_is_admin_or_superuser_allows_admin(self):
        admin_user = create_feedback_admin_user()
        request = self.factory.get("/api/feedback/requests/admin/")
        request.user = admin_user

        permission = IsAdminOrSuperuser()
        self.assertTrue(permission.has_permission(request, view=None))

    def test_is_admin_or_superuser_denies_regular_user(self):
        user = create_feedback_user()
        request = self.factory.get("/api/feedback/requests/admin/")
        request.user = user

        permission = IsAdminOrSuperuser()
        self.assertFalse(permission.has_permission(request, view=None))

    def test_is_feedback_owner_or_admin_allows_owner(self):
        user = create_feedback_user()
        feedback_request = create_feedback_request(user=user)

        request = self.factory.get("/api/feedback/requests/my/1/")
        request.user = user

        permission = IsFeedbackOwnerOrAdmin()
        self.assertTrue(
            permission.has_object_permission(request, view=None, obj=feedback_request)
        )

    def test_is_feedback_owner_or_admin_allows_admin(self):
        admin_user = create_feedback_admin_user()
        user = create_feedback_user()
        feedback_request = create_feedback_request(user=user)

        request = self.factory.get("/api/feedback/requests/admin/1/")
        request.user = admin_user

        permission = IsFeedbackOwnerOrAdmin()
        self.assertTrue(
            permission.has_object_permission(request, view=None, obj=feedback_request)
        )

    def test_is_feedback_owner_or_admin_denies_other_user(self):
        owner = create_feedback_user(email="owner@example.com")
        other_user = create_feedback_user(email="other@example.com")
        feedback_request = create_feedback_request(user=owner)

        request = self.factory.get("/api/feedback/requests/my/1/")
        request.user = other_user

        permission = IsFeedbackOwnerOrAdmin()
        self.assertFalse(
            permission.has_object_permission(request, view=None, obj=feedback_request)
        )
