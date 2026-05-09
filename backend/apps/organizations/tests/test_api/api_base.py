from __future__ import annotations

from rest_framework.test import APITestCase

from apps.users.tests.factories import create_admin_user


class OrganizationApiBaseTestCase(APITestCase):
    """Базовый класс для API-тестов organizations."""

    def setUp(self):
        self.admin_user = create_admin_user()
        self.client.force_authenticate(user=self.admin_user)
