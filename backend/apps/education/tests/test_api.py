from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.education.tests.factories import (
    create_academic_year,
    create_curriculum,
    create_curriculum_item,
    create_education_period,
    create_group_subject,
    create_student_group_enrollment,
    create_teacher_group_subject,
)
from apps.organizations.tests.factories import create_group, create_subject
from apps.users.tests.factories import create_admin_user


class EducationApiTestCase(APITestCase):
    def setUp(self):
        self.admin_user = create_admin_user()
        self.client.force_authenticate(user=self.admin_user)

    def test_academic_year_list(self):
        create_academic_year(name="2025/2026")

        url = reverse("education:academic-year-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_education_period_list(self):
        create_education_period()

        url = reverse("education:education-period-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_list(self):
        create_student_group_enrollment()

        url = reverse("education:student-group-enrollment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_group_subject_list(self):
        create_group_subject()

        url = reverse("education:group-subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_group_subject_list(self):
        create_teacher_group_subject()

        url = reverse("education:teacher-group-subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_curriculum_list(self):
        create_curriculum()

        url = reverse("education:curriculum-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_curriculum_item_list(self):
        create_curriculum_item()

        url = reverse("education:curriculum-item-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_academic_year(self):
        url = reverse("education:academic-year-list")
        payload = {
            "name": "2035/2036",
            "start_date": "2035-09-01",
            "end_date": "2036-06-30",
            "is_current": False,
            "is_active": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "2035/2036")

    def test_create_group_subject(self):
        academic_year = create_academic_year(name="2036/2037", start_date="2036-09-01", end_date="2037-06-30")
        period = create_education_period(
            academic_year=academic_year,
            start_date="2036-09-01",
            end_date="2036-12-31",
        )
        group = create_group()
        subject = create_subject()

        url = reverse("education:group-subject-list")
        payload = {
            "group_id": group.id,
            "subject_id": subject.id,
            "academic_year_id": academic_year.id,
            "period_id": period.id,
            "planned_hours": 72,
            "contact_hours": 48,
            "independent_hours": 24,
            "assessment_type": "exam",
            "is_required": True,
            "is_active": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["planned_hours"], 72)
