from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.education.services import (
    assign_teacher_group_subject,
    create_group_subject,
    create_student_group_enrollment,
)
from apps.education.tests.factories import (
    create_academic_year,
    create_education_period,
    create_group_subject as create_group_subject_factory,
    create_student_user,
    create_teacher_user,
)
from apps.organizations.tests.factories import (
    create_group,
    create_subject,
    create_teacher_organization,
    create_teacher_subject,
)
from apps.users.tests.factories import create_user


class EnrollmentServicesTestCase(TestCase):
    def test_create_student_group_enrollment_for_student(self):
        student = create_student_user()
        group = create_group()
        academic_year = create_academic_year()

        enrollment = create_student_group_enrollment(
            student=student,
            group=group,
            academic_year=academic_year,
            enrollment_date=date(2025, 9, 1),
        )

        self.assertEqual(enrollment.student, student)
        self.assertEqual(enrollment.group, group)

    def test_create_student_group_enrollment_for_non_student_raises_error(self):
        user = create_user(email="not_student@example.com", password="TestPass123!")
        group = create_group()
        academic_year = create_academic_year()

        with self.assertRaises(ValidationError):
            create_student_group_enrollment(
                student=user,
                group=group,
                academic_year=academic_year,
                enrollment_date=date(2025, 9, 1),
            )


class LoadServicesTestCase(TestCase):
    def test_create_group_subject_with_valid_period(self):
        academic_year = create_academic_year()
        period = create_education_period(
            academic_year=academic_year,
            start_date=academic_year.start_date,
            end_date=date(2025, 12, 31),
        )
        group = create_group()
        subject = create_subject()

        group_subject = create_group_subject(
            group=group,
            subject=subject,
            academic_year=academic_year,
            period=period,
            planned_hours=72,
            contact_hours=48,
            independent_hours=24,
        )

        self.assertEqual(group_subject.period, period)

    def test_create_group_subject_with_invalid_period_raises_error(self):
        academic_year_1 = create_academic_year(name="2025/2026")
        academic_year_2 = create_academic_year(
            name="2026/2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
        )
        period = create_education_period(
            academic_year=academic_year_2,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 31),
        )
        group = create_group()
        subject = create_subject()

        with self.assertRaises(ValidationError):
            create_group_subject(
                group=group,
                subject=subject,
                academic_year=academic_year_1,
                period=period,
            )

    def test_assign_teacher_group_subject(self):
        teacher = create_teacher_user()
        group_subject = create_group_subject_factory()

        create_teacher_organization(
            teacher=teacher,
            organization=group_subject.group.organization,
            is_primary=True,
        )
        create_teacher_subject(
            teacher=teacher,
            subject=group_subject.subject,
            is_primary=True,
        )

        assignment = assign_teacher_group_subject(
            teacher=teacher,
            group_subject=group_subject,
            is_primary=True,
            starts_at=date(2025, 9, 1),
            ends_at=date(2025, 12, 31),
        )

        self.assertEqual(assignment.teacher, teacher)
        self.assertEqual(assignment.group_subject, group_subject)

    def test_assign_non_teacher_group_subject_raises_error(self):
        user = create_user(email="not_teacher@example.com", password="TestPass123!")
        group_subject = create_group_subject_factory()

        with self.assertRaises(ValidationError):
            assign_teacher_group_subject(
                teacher=user,
                group_subject=group_subject,
            )
