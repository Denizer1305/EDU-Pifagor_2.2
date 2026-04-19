from __future__ import annotations

from django.test import TestCase

from apps.users.selectors.user_selectors import get_user_by_email, get_users_queryset
from apps.users.tests.factories import create_profile, create_user


class UserSelectorsTestCase(TestCase):
    def test_get_user_by_email(self):
        user = create_user(email="selector@example.com", password="TestPass123!")
        create_profile(user=user, email="selector@example.com")

        found = get_user_by_email("selector@example.com")

        self.assertIsNotNone(found)
        self.assertEqual(found.id, user.id)

    def test_get_users_queryset(self):
        user = create_user(email="selector2@example.com", password="TestPass123!")
        create_profile(user=user, email="selector2@example.com")

        qs = get_users_queryset()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().email, "selector2@example.com")
