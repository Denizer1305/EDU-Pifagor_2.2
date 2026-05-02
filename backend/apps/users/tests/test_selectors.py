from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_organization,
)
from apps.users.constants import (
    LINK_STATUS_PENDING,
    ONBOARDING_STATUS_PENDING,
    ROLE_STUDENT,
    ROLE_TEACHER,
    VERIFICATION_STATUS_PENDING,
)
from apps.users.models import ParentStudent, Role
from apps.users.selectors import (
    get_parent_profiles_queryset,
    get_parent_student_links_queryset,
    get_pending_parent_student_links_queryset,
    get_pending_student_profiles_queryset,
    get_pending_teacher_profiles_queryset,
    get_pending_users_queryset,
    get_profile_by_user_id,
    get_profiles_queryset,
    get_role_by_code_selector,
    get_roles_queryset,
    get_student_profile_by_user_id,
    get_student_profiles_queryset,
    get_teacher_profile_by_user_id,
    get_teacher_profiles_queryset,
    get_user_roles_queryset,
    get_user_with_related,
    get_users_queryset,
)
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
)
from apps.users.services.role_services import assign_role_to_user

User = get_user_model()


def _relation_type_mother():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.MOTHER
    return ParentStudent.RelationType.MOTHER


def _relation_type_father():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.FATHER
    return ParentStudent.RelationType.FATHER


class BaseUsersSelectorTestCase(TestCase):
    def create_user(self, email: str, registration_type: str = "student"):
        user = User.objects.create_user(
            email=email,
            password="StrongPass123!",
            registration_type=registration_type,
        )
        profile = get_or_create_base_profile(user)
        profile.first_name = "Иван"
        profile.last_name = email.split("@")[0].capitalize()
        profile.full_clean()
        profile.save()
        ensure_role_profile(user)
        return user


class UserSelectorsTestCase(BaseUsersSelectorTestCase):
    def test_get_users_queryset_by_search(self):
        user = self.create_user("student1@example.com")
        queryset = get_users_queryset(search="student1")
        self.assertIn(user, queryset)

    def test_get_pending_users_queryset(self):
        user = self.create_user("pending@example.com")
        user.onboarding_status = ONBOARDING_STATUS_PENDING
        user.save(update_fields=["onboarding_status", "updated_at"])

        queryset = get_pending_users_queryset()
        self.assertIn(user, queryset)

    def test_get_user_with_related(self):
        user = self.create_user("related@example.com")
        result = get_user_with_related(user.id)
        self.assertEqual(result.id, user.id)
        self.assertIsNotNone(result.profile)


class ProfileSelectorsTestCase(BaseUsersSelectorTestCase):
    def test_get_profiles_queryset(self):
        user = self.create_user("profile1@example.com")
        queryset = get_profiles_queryset(search="profile1")
        self.assertIn(user.profile, queryset)

    def test_get_profile_by_user_id(self):
        user = self.create_user("profile2@example.com")
        profile = get_profile_by_user_id(user.id)
        self.assertEqual(profile.user_id, user.id)


class RoleSelectorsTestCase(BaseUsersSelectorTestCase):
    def setUp(self):
        self.student_role = Role.objects.create(
            code=ROLE_STUDENT,
            name="Студент",
            is_active=True,
        )
        self.teacher_role = Role.objects.create(
            code=ROLE_TEACHER,
            name="Преподаватель",
            is_active=True,
        )

    def test_get_roles_queryset(self):
        queryset = get_roles_queryset(search="Студ")
        self.assertIn(self.student_role, queryset)

    def test_get_role_by_code_selector(self):
        role = get_role_by_code_selector(ROLE_STUDENT)
        self.assertEqual(role.id, self.student_role.id)

    def test_get_user_roles_queryset(self):
        user = self.create_user("roles@example.com")
        assign_role_to_user(user, ROLE_STUDENT)

        queryset = get_user_roles_queryset(user_id=user.id, role_code=ROLE_STUDENT)
        self.assertEqual(queryset.count(), 1)


class StudentSelectorsTestCase(BaseUsersSelectorTestCase):
    def setUp(self):
        self.organization = create_organization(
            name="Организация селекторов", short_name="ОргС"
        )
        self.department = create_department(
            organization=self.organization,
            name="Отделение селекторов",
            short_name="ОтдС",
        )
        self.group = create_group(
            organization=self.organization,
            department=self.department,
            name="Группа селекторов",
            code="GR-SEL-01",
        )

    def test_get_student_profiles_queryset(self):
        user = self.create_user(
            "student-selector@example.com", registration_type="student"
        )
        profile = user.student_profile
        profile.requested_organization = self.organization
        profile.requested_department = self.department
        profile.requested_group = self.group
        profile.verification_status = VERIFICATION_STATUS_PENDING
        profile.save()

        queryset = get_student_profiles_queryset(search="student-selector")
        self.assertIn(profile, queryset)

    def test_get_pending_student_profiles_queryset(self):
        user = self.create_user(
            "student-pending@example.com", registration_type="student"
        )
        profile = user.student_profile
        profile.verification_status = VERIFICATION_STATUS_PENDING
        profile.save()

        queryset = get_pending_student_profiles_queryset()
        self.assertIn(profile, queryset)

    def test_get_student_profile_by_user_id(self):
        user = self.create_user(
            "student-by-user@example.com", registration_type="student"
        )
        profile = get_student_profile_by_user_id(user.id)
        self.assertEqual(profile.user_id, user.id)


class TeacherSelectorsTestCase(BaseUsersSelectorTestCase):
    def setUp(self):
        self.organization = create_organization(
            name="Организация преподов", short_name="ОргП"
        )
        self.department = create_department(
            organization=self.organization,
            name="Отделение преподов",
            short_name="ОтдП",
        )

    def test_get_teacher_profiles_queryset(self):
        user = self.create_user(
            "teacher-selector@example.com", registration_type="teacher"
        )
        profile = user.teacher_profile
        profile.requested_organization = self.organization
        profile.requested_department = self.department
        profile.verification_status = VERIFICATION_STATUS_PENDING
        if hasattr(profile, "position"):
            profile.position = "Преподаватель математики"
        profile.save()

        queryset = get_teacher_profiles_queryset(search="teacher-selector")
        self.assertIn(profile, queryset)

    def test_get_pending_teacher_profiles_queryset(self):
        user = self.create_user(
            "teacher-pending@example.com", registration_type="teacher"
        )
        profile = user.teacher_profile
        profile.verification_status = VERIFICATION_STATUS_PENDING
        profile.save()

        queryset = get_pending_teacher_profiles_queryset()
        self.assertIn(profile, queryset)

    def test_get_teacher_profile_by_user_id(self):
        user = self.create_user(
            "teacher-by-user@example.com", registration_type="teacher"
        )
        profile = get_teacher_profile_by_user_id(user.id)
        self.assertEqual(profile.user_id, user.id)


class ParentSelectorsTestCase(BaseUsersSelectorTestCase):
    def test_get_parent_profiles_queryset(self):
        user = self.create_user(
            "parent-selector@example.com", registration_type="parent"
        )
        queryset = get_parent_profiles_queryset(search="parent-selector")
        self.assertIn(user.parent_profile, queryset)

    def test_get_parent_student_links_queryset(self):
        parent = self.create_user("parent-link@example.com", registration_type="parent")
        student = self.create_user(
            "student-link@example.com", registration_type="student"
        )

        link = ParentStudent.objects.create(
            parent=parent,
            student=student,
            relation_type=_relation_type_mother(),
            status=LINK_STATUS_PENDING,
            requested_by=parent,
        )

        queryset = get_parent_student_links_queryset(parent_id=parent.id)
        self.assertIn(link, queryset)

    def test_get_pending_parent_student_links_queryset(self):
        parent = self.create_user(
            "parent-pending@example.com", registration_type="parent"
        )
        student = self.create_user(
            "student-pending-link@example.com", registration_type="student"
        )

        link = ParentStudent.objects.create(
            parent=parent,
            student=student,
            relation_type=_relation_type_father(),
            status=LINK_STATUS_PENDING,
            requested_by=parent,
        )

        queryset = get_pending_parent_student_links_queryset()
        self.assertIn(link, queryset)
