from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase

from apps.organizations.selectors import (
    get_active_teacher_organizations_queryset,
    get_teacher_organizations_queryset,
    get_teacher_subjects_queryset,
)
from apps.organizations.tests.factories import (
    create_organization,
    create_subject,
    create_teacher_organization,
    create_teacher_subject,
    create_teacher_user,
)


class TeacherOrganizationSelectorsTestCase(TestCase):
    def test_get_teacher_organizations_queryset(self):
        teacher = create_teacher_user()
        organization = create_organization()

        create_teacher_organization(
            teacher=teacher,
            organization=organization,
        )

        queryset = get_teacher_organizations_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_teacher_organizations_queryset(self):
        teacher = create_teacher_user()

        active_link = create_teacher_organization(
            teacher=teacher,
            organization=create_organization(
                name="Орг А",
                short_name="А",
            ),
            is_active=True,
            starts_at=date.today() - timedelta(days=1),
            ends_at=date.today() + timedelta(days=1),
        )
        create_teacher_organization(
            teacher=teacher,
            organization=create_organization(
                name="Орг Б",
                short_name="Б",
            ),
            is_active=False,
            starts_at=date.today() - timedelta(days=10),
            ends_at=date.today() - timedelta(days=1),
        )

        queryset = get_active_teacher_organizations_queryset(
            teacher_id=teacher.id,
        )

        self.assertEqual(queryset.count(), 1)
        self.assertIn(active_link, queryset)


class TeacherSubjectSelectorsTestCase(TestCase):
    def test_get_teacher_subjects_queryset(self):
        teacher = create_teacher_user()
        subject = create_subject()

        create_teacher_subject(
            teacher=teacher,
            subject=subject,
        )

        queryset = get_teacher_subjects_queryset()

        self.assertEqual(queryset.count(), 1)
