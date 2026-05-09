from __future__ import annotations

from django.test import TestCase

from apps.organizations.selectors import (
    get_active_subject_categories_queryset,
    get_active_subjects_queryset,
    get_subject_categories_queryset,
    get_subjects_queryset,
)
from apps.organizations.tests.factories import (
    create_subject,
    create_subject_category,
)


class SubjectCategorySelectorsTestCase(TestCase):
    def test_get_subject_categories_queryset(self):
        create_subject_category(
            code="math",
            name="Математика",
        )

        queryset = get_subject_categories_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_subject_categories_queryset(self):
        create_subject_category(
            code="active_math",
            name="Активная математика",
            is_active=True,
        )
        create_subject_category(
            code="inactive_math",
            name="Неактивная математика",
            is_active=False,
        )

        queryset = get_active_subject_categories_queryset()

        self.assertEqual(queryset.count(), 1)


class SubjectSelectorsTestCase(TestCase):
    def test_get_subjects_queryset(self):
        create_subject(name="Алгебра")

        queryset = get_subjects_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_subjects_queryset(self):
        create_subject(
            name="Активный предмет",
            short_name="Акт",
            is_active=True,
        )
        create_subject(
            name="Неактивный предмет",
            short_name="Неакт",
            is_active=False,
        )

        queryset = get_active_subjects_queryset()

        self.assertEqual(queryset.count(), 1)
