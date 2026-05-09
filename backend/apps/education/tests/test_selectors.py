from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.education.selectors import (
    get_academic_years_queryset,
    get_active_academic_years_queryset,
    get_active_curricula_queryset,
    get_active_curriculum_items_queryset,
    get_active_education_periods_queryset,
    get_active_group_subjects_queryset,
    get_active_student_group_enrollments_queryset,
    get_active_teacher_group_subjects_queryset,
    get_curricula_queryset,
    get_curriculum_items_queryset,
    get_education_periods_queryset,
    get_group_subjects_queryset,
    get_student_group_enrollments_queryset,
    get_teacher_group_subjects_queryset,
)
from apps.education.tests.factories import (
    create_academic_year,
    create_curriculum,
    create_curriculum_item,
    create_education_period,
    create_group_subject,
    create_student_group_enrollment,
    create_teacher_group_subject,
)


class AcademicSelectorsTestCase(TestCase):
    def test_get_academic_years_queryset(self):
        create_academic_year(name="2025/2026")
        queryset = get_academic_years_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_academic_years_queryset(self):
        create_academic_year(name="2025/2026", is_active=True)
        create_academic_year(
            name="2026/2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
            is_active=False,
        )

        queryset = get_active_academic_years_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_education_periods_queryset(self):
        create_education_period()
        queryset = get_education_periods_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_education_periods_queryset(self):
        create_education_period(is_active=True)
        create_education_period(
            academic_year=create_academic_year(
                name="2028/2029",
                start_date=date(2028, 9, 1),
                end_date=date(2029, 6, 30),
            ),
            is_active=False,
            start_date=date(2028, 9, 1),
            end_date=date(2028, 12, 31),
        )

        queryset = get_active_education_periods_queryset()
        self.assertEqual(queryset.count(), 1)


class EnrollmentSelectorsTestCase(TestCase):
    def test_get_student_group_enrollments_queryset(self):
        create_student_group_enrollment()
        queryset = get_student_group_enrollments_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_student_group_enrollments_queryset(self):
        active_enrollment = create_student_group_enrollment(status="active")

        create_student_group_enrollment(
            student=active_enrollment.student,
            group=active_enrollment.group,
            academic_year=create_academic_year(
                name="2034/2035",
                start_date=date(2034, 9, 1),
                end_date=date(2035, 6, 30),
            ),
            status="active",
            journal_number=2,
        )

        queryset = get_active_student_group_enrollments_queryset()

        self.assertGreaterEqual(queryset.count(), 1)
        self.assertIn(active_enrollment, queryset)


class LoadSelectorsTestCase(TestCase):
    def test_get_group_subjects_queryset(self):
        create_group_subject()
        queryset = get_group_subjects_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_group_subjects_queryset(self):
        create_group_subject(is_active=True)
        create_group_subject(
            academic_year=create_academic_year(
                name="2030/2031",
                start_date=date(2030, 9, 1),
                end_date=date(2031, 6, 30),
            ),
            period=create_education_period(
                academic_year=create_academic_year(
                    name="2031/2032",
                    start_date=date(2031, 9, 1),
                    end_date=date(2032, 6, 30),
                ),
                start_date=date(2032, 9, 1),
                end_date=date(2032, 12, 31),
            ),
            is_active=False,
        )
        queryset = get_active_group_subjects_queryset()

        self.assertGreaterEqual(queryset.count(), 1)

    def test_get_teacher_group_subjects_queryset(self):
        create_teacher_group_subject()
        queryset = get_teacher_group_subjects_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_teacher_group_subjects_queryset(self):
        create_teacher_group_subject(is_active=True)
        queryset = get_active_teacher_group_subjects_queryset()

        self.assertEqual(queryset.count(), 1)


class CurriculumSelectorsTestCase(TestCase):
    def test_get_curricula_queryset(self):
        create_curriculum()
        queryset = get_curricula_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_curricula_queryset(self):
        create_curriculum(is_active=True)
        create_curriculum(
            academic_year=create_academic_year(
                name="2032/2033",
                start_date=date(2032, 9, 1),
                end_date=date(2033, 6, 30),
            ),
            is_active=False,
        )
        queryset = get_active_curricula_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_curriculum_items_queryset(self):
        create_curriculum_item()
        queryset = get_curriculum_items_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_curriculum_items_queryset(self):
        create_curriculum_item(is_active=True)
        queryset = get_active_curriculum_items_queryset()

        self.assertEqual(queryset.count(), 1)
