from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.organizations.tests.test_api.api_base import OrganizationApiBaseTestCase
from apps.organizations.tests.factories import (
    create_subject,
    create_subject_category,
)


class OrganizationCatalogApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API справочников предметов."""

    def test_subject_category_list(self):
        create_subject_category(code="math", name="Математика")

        url = reverse("organizations:subject-category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subject_list(self):
        create_subject(name="Алгебра", short_name="Алгебра")

        url = reverse("organizations:subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
