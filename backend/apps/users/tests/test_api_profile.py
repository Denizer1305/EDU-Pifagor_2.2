from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_organization,
)
from apps.users.constants import (
    LINK_STATUS_APPROVED,
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_REJECTED,
    ROLE_PARENT,
    ROLE_STUDENT,
    ROLE_TEACHER,
    VERIFICATION_STATUS_APPROVED,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
)
from apps.users.models import ParentStudent, Role
from apps.users.services.profile_services import ensure_role_profile, get_or_create_base_profile

User = get_user_model()


def _relation_type_mother():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.MOTHER
    return ParentStudent.RelationType.MOTHER


def _relation_type_father():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.FATHER
    return ParentStudent.RelationType.FATHER


class ProfileApiTestCase(APITestCase):
    def setUp(self):
        self._ensure_system_roles()

        self.organization = create_organization(
            name="Профильная организация",
            short_name="ПрофОрг",
        )
        self.department = create_department(
            organization=self.organization,
            name="Профильное отделение",
            short_name="ПрофОтд",
        )
        self.group = create_group(
            organization=self.organization,
            department=self.department,
            name="Профильная группа",
            code="PROF-01",
        )

        self.admin = User.objects.create_superuser(
            email="admin-profile@example.com",
            password="StrongPass123!",
        )
        admin_profile = get_or_create_base_profile(self.admin)
        admin_profile.first_name = "Админ"
        admin_profile.last_name = "Системный"
        admin_profile.full_clean()
        admin_profile.save()

        self.student = self.create_user(
            "student-profile@example.com",
            registration_type="student",
        )
        self.teacher = self.create_user(
            "teacher-profile@example.com",
            registration_type="teacher",
        )
        self.parent = self.create_user(
            "parent-profile@example.com",
            registration_type="parent",
        )

        self.set_group_code(self.group)
        self.set_teacher_code(self.organization)

    def _ensure_system_roles(self):
        Role.objects.get_or_create(code=ROLE_STUDENT, defaults={"name": "Студент", "is_active": True})
        Role.objects.get_or_create(code=ROLE_TEACHER, defaults={"name": "Преподаватель", "is_active": True})
        Role.objects.get_or_create(code=ROLE_PARENT, defaults={"name": "Родитель", "is_active": True})

    def create_user(
        self,
        email: str,
        registration_type: str = "student",
        password: str = "StrongPass123!",
    ):
        user = User.objects.create_user(
            email=email,
            password=password,
            registration_type=registration_type,
        )
        profile = get_or_create_base_profile(user)
        profile.first_name = "Иван"
        profile.last_name = email.split("@")[0].capitalize()
        profile.full_clean()
        profile.save()
        ensure_role_profile(user)
        return user

    def set_group_code(self, group, code: str = "group-secret"):
        if hasattr(group, "join_code_hash"):
            group.join_code_hash = make_password(code)
        if hasattr(group, "join_code_is_active"):
            group.join_code_is_active = True
        if hasattr(group, "join_code_expires_at"):
            group.join_code_expires_at = timezone.now() + timedelta(days=1)
        group.save()
        return code

    def set_teacher_code(self, organization, code: str = "teacher-secret"):
        if hasattr(organization, "teacher_registration_code_hash"):
            organization.teacher_registration_code_hash = make_password(code)
        if hasattr(organization, "teacher_registration_code_is_active"):
            organization.teacher_registration_code_is_active = True
        if hasattr(organization, "teacher_registration_code_expires_at"):
            organization.teacher_registration_code_expires_at = timezone.now() + timedelta(days=1)
        organization.save()
        return code

    def test_my_profile_get(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("users:my-profile")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.student.email)

    def test_my_profile_patch(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("users:my-profile")

        payload = {
            "first_name": "Обновленное",
            "last_name": "Имя",
            "city": "Москва",
            "phone": "+79995554433",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.profile.refresh_from_db()
        self.assertEqual(self.student.profile.city, "Москва")
        self.assertEqual(self.student.profile.first_name, "Обновленное")

    def test_student_onboarding_submits_request(self):
        self.student.is_email_verified = True
        self.student.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.student)
        url = reverse("users:student-onboarding")

        payload = {
            "requested_organization_id": self.organization.id,
            "requested_department_id": self.department.id,
            "requested_group_id": self.group.id,
            "submitted_group_code": "group-secret",
            "student_code": "ST-001",
            "notes": "Хочу привязаться к группе",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.student.refresh_from_db()

        self.assertEqual(
            self.student.student_profile.verification_status,
            VERIFICATION_STATUS_PENDING,
        )
        self.assertEqual(self.student.student_profile.requested_group_id, self.group.id)

    def test_student_profile_review_approve(self):
        self.student.student_profile.requested_organization = self.organization
        self.student.student_profile.requested_department = self.department
        self.student.student_profile.requested_group = self.group
        self.student.student_profile.submitted_group_code = "group-secret"
        self.student.student_profile.verification_status = VERIFICATION_STATUS_PENDING
        self.student.student_profile.save()

        self.student.is_email_verified = True
        self.student.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.admin)
        url = reverse("users:student-profile-review", args=[self.student.student_profile.id])

        payload = {
            "verification_status": VERIFICATION_STATUS_APPROVED,
            "verification_comment": "Подтверждено куратором",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.student.refresh_from_db()

        self.assertEqual(self.student.student_profile.verification_status, VERIFICATION_STATUS_APPROVED)
        self.assertEqual(self.student.onboarding_status, ONBOARDING_STATUS_ACTIVE)
        self.assertTrue(self.student.user_roles.filter(role__code=ROLE_STUDENT).exists())

    def test_student_profile_review_reject(self):
        self.student.student_profile.verification_status = VERIFICATION_STATUS_PENDING
        self.student.student_profile.save()

        self.client.force_authenticate(user=self.admin)
        url = reverse("users:student-profile-review", args=[self.student.student_profile.id])

        payload = {
            "verification_status": VERIFICATION_STATUS_REJECTED,
            "verification_comment": "Неверный код группы",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.student.refresh_from_db()

        self.assertEqual(self.student.student_profile.verification_status, VERIFICATION_STATUS_REJECTED)
        self.assertEqual(self.student.onboarding_status, ONBOARDING_STATUS_REJECTED)

    def test_teacher_onboarding_submits_request(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("users:teacher-onboarding")

        payload = {
            "requested_organization_id": self.organization.id,
            "requested_department_id": self.department.id,
            "position": "Преподаватель информатики",
            "employee_code": "EMP-777",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.teacher.teacher_profile.refresh_from_db()
        self.assertEqual(self.teacher.teacher_profile.verification_status, VERIFICATION_STATUS_PENDING)

    def test_teacher_profile_review_approve(self):
        self.teacher.teacher_profile.requested_organization = self.organization
        self.teacher.teacher_profile.requested_department = self.department
        self.teacher.teacher_profile.verification_status = VERIFICATION_STATUS_PENDING
        self.teacher.teacher_profile.save()

        self.teacher.is_email_verified = True
        self.teacher.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.admin)
        url = reverse("users:teacher-profile-review", args=[self.teacher.teacher_profile.id])

        payload = {
            "verification_status": VERIFICATION_STATUS_APPROVED,
            "verification_comment": "Подтвержден как преподаватель",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.teacher.teacher_profile.refresh_from_db()
        self.teacher.refresh_from_db()

        self.assertEqual(self.teacher.teacher_profile.verification_status, VERIFICATION_STATUS_APPROVED)
        self.assertEqual(self.teacher.onboarding_status, ONBOARDING_STATUS_ACTIVE)
        self.assertTrue(self.teacher.user_roles.filter(role__code=ROLE_TEACHER).exists())

    def test_parent_student_create_request(self):
        self.client.force_authenticate(user=self.parent)
        url = reverse("users:parent-student-link-request")

        payload = {
            "student_user_id": self.student.id,
            "relation_type": _relation_type_mother(),
            "comment": "Мама ученика",
            "is_primary": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        link = ParentStudent.objects.get(parent=self.parent, student=self.student)
        self.assertEqual(link.status, "pending")

    def test_parent_student_review_approve(self):
        link = ParentStudent.objects.create(
            parent=self.parent,
            student=self.student,
            relation_type=_relation_type_father(),
            status="pending",
            requested_by=self.parent,
        )

        self.parent.is_email_verified = True
        self.parent.save(update_fields=["is_email_verified"])

        self.client.force_authenticate(user=self.admin)
        url = reverse("users:parent-student-link-review", args=[link.id])

        payload = {
            "status": LINK_STATUS_APPROVED,
            "comment": "Связь подтверждена",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        link.refresh_from_db()
        self.parent.refresh_from_db()

        self.assertEqual(link.status, LINK_STATUS_APPROVED)
        self.assertEqual(self.parent.onboarding_status, ONBOARDING_STATUS_ACTIVE)
        self.assertTrue(self.parent.user_roles.filter(role__code=ROLE_PARENT).exists())
