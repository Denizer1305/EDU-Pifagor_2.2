from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.education.models import (
    AcademicYear,
    EducationPeriod,
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


class AcademicYearModelTestCase(TestCase):
    def test_create_academic_year(self):
        academic_year = create_academic_year(name="2025/2026")

        self.assertEqual(academic_year.name, "2025/2026")
        self.assertEqual(str(academic_year), "2025/2026")

    def test_academic_year_end_date_must_be_after_start_date(self):
        academic_year = AcademicYear(
            name="2025/2026",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 1),
        )

        with self.assertRaises(ValidationError):
            academic_year.clean()


class EducationPeriodModelTestCase(TestCase):
    def test_create_education_period(self):
        period = create_education_period(name="1 семестр", code="SEM-1")

        self.assertEqual(period.name, "1 семестр")
        self.assertIn("1 семестр", str(period))

    def test_period_must_be_inside_academic_year(self):
        academic_year = create_academic_year(
            start_date=date(2025, 9, 1),
            end_date=date(2026, 6, 30),
        )
        period = EducationPeriod(
            academic_year=academic_year,
            name="Ошибка",
            code="ERR-1",
            sequence=1,
            start_date=date(2025, 8, 1),
            end_date=date(2025, 12, 31),
        )

        with self.assertRaises(ValidationError):
            period.clean()


class StudentGroupEnrollmentModelTestCase(TestCase):
    def test_create_student_group_enrollment(self):
        enrollment = create_student_group_enrollment()

        self.assertTrue(enrollment.is_primary)
        self.assertEqual(enrollment.status, enrollment.StatusChoices.ACTIVE)


class GroupSubjectModelTestCase(TestCase):
    def test_create_group_subject(self):
        group_subject = create_group_subject()

        self.assertEqual(group_subject.planned_hours, 72)
        self.assertTrue(group_subject.is_required)

    def test_group_subject_period_must_belong_to_same_academic_year(self):
        academic_year_1 = create_academic_year(name="2025/2026")
        academic_year_2 = create_academic_year(
            name="2026/2027", start_date=date(2026, 9, 1), end_date=date(2027, 6, 1)
        )

        period = create_education_period(
            academic_year=academic_year_2,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 31),
        )
        group_subject = create_group_subject(
            academic_year=academic_year_1,
            period=period,
        )

        with self.assertRaises(ValidationError):
            group_subject.clean()


class TeacherGroupSubjectModelTestCase(TestCase):
    def test_create_teacher_group_subject(self):
        assignment = create_teacher_group_subject()

        self.assertTrue(assignment.is_primary)
        self.assertTrue(assignment.is_active)


class CurriculumModelTestCase(TestCase):
    def test_create_curriculum(self):
        curriculum = create_curriculum()

        self.assertIn("Учебный план", curriculum.name)

    def test_create_curriculum_item(self):
        item = create_curriculum_item()

        self.assertEqual(item.sequence, 1)
        self.assertTrue(item.is_required)

    def test_curriculum_item_period_must_belong_to_same_academic_year(self):
        curriculum = create_curriculum()
        other_year = create_academic_year(
            name="2028/2029",
            start_date=date(2028, 9, 1),
            end_date=date(2029, 6, 30),
        )
        other_period = create_education_period(
            academic_year=other_year,
            start_date=date(2028, 9, 1),
            end_date=date(2028, 12, 31),
        )

        item = create_curriculum_item(
            curriculum=curriculum,
            period=other_period,
        )

        with self.assertRaises(ValidationError):
            item.clean()
