from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone

from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_organization,
)
from apps.users.constants import (
    LINK_STATUS_APPROVED,
    LINK_STATUS_PENDING,
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
from apps.users.services.auth_services import (
    authenticate_user,
    build_password_reset_token,
    build_verify_email_token,
    change_user_password,
    register_user,
    reset_password_by_token,
    verify_user_email_by_token,
)
from apps.users.services.parent_services import (
    approve_parent_student_link,
    create_parent_student_link_request,
    reject_parent_student_link,
)
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
    update_base_profile,
)
from apps.users.services.role_services import (
    assign_role_to_user,
    list_user_role_codes,
    remove_role_from_user,
    user_has_role,
)
from apps.users.services.student_services import (
    approve_student_profile,
    reject_student_profile,
    submit_student_group_request,
)
from apps.users.services.teacher_services import (
    approve_teacher_profile,
    reject_teacher_profile,
    submit_teacher_verification_request,
)
from apps.users.services.user_services import (
    activate_user_onboarding,
    block_user,
    mark_user_email_verified,
    reject_user_onboarding,
)

User = get_user_model()


def _relation_type_mother():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.MOTHER
    return ParentStudent.RelationType.MOTHER


def _relation_type_father():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.FATHER
    return ParentStudent.RelationType.FATHER


def _relation_type_guardian():
    if hasattr(ParentStudent, "RelationTypeChoices"):
        return ParentStudent.RelationTypeChoices.GUARDIAN
    return ParentStudent.RelationType.GUARDIAN


class BaseUsersServiceTestCase(TestCase):
    def setUp(self):
        Role.objects.get_or_create(code=ROLE_STUDENT, defaults={"name": "Студент", "is_active": True})
        Role.objects.get_or_create(code=ROLE_TEACHER, defaults={"name": "Преподаватель", "is_active": True})
        Role.objects.get_or_create(code=ROLE_PARENT, defaults={"name": "Родитель", "is_active": True})

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

    def create_org_stack(self):
        organization = create_organization(name="Сервисная организация", short_name="СервОрг")
        department = create_department(
            organization=organization,
            name="Сервисное отделение",
            short_name="СервОтд",
        )
        group = create_group(
            organization=organization,
            department=department,
            name="Сервисная группа",
            code="SERV-01",
        )
        return organization, department, group

    def set_teacher_code(self, organization, code="teacher-secret"):
        if hasattr(organization, "teacher_registration_code_hash"):
            organization.teacher_registration_code_hash = make_password(code)
        if hasattr(organization, "teacher_registration_code_is_active"):
            organization.teacher_registration_code_is_active = True
        if hasattr(organization, "teacher_registration_code_expires_at"):
            organization.teacher_registration_code_expires_at = timezone.now() + timedelta(days=1)
        organization.save()
        return code

    def set_group_code(self, group, code="group-secret"):
        if hasattr(group, "join_code_hash"):
            group.join_code_hash = make_password(code)
        if hasattr(group, "join_code_is_active"):
            group.join_code_is_active = True
        if hasattr(group, "join_code_expires_at"):
            group.join_code_expires_at = timezone.now() + timedelta(days=1)
        group.save()
        return code


class AuthServicesTestCase(BaseUsersServiceTestCase):
    def test_register_student_user(self):
        user = register_user(
            email="student-register@example.com",
            password="StrongPass123!",
            password_repeat="StrongPass123!",
            registration_type="student",
            first_name="Иван",
            last_name="Студентов",
        )

        self.assertEqual(user.registration_type, "student")
        self.assertTrue(hasattr(user, "student_profile"))

    def test_register_teacher_user(self):
        organization, department, _ = self.create_org_stack()
        teacher_code = self.set_teacher_code(organization)

        user = register_user(
            email="teacher-register@example.com",
            password="StrongPass123!",
            password_repeat="StrongPass123!",
            registration_type="teacher",
            first_name="Петр",
            last_name="Преподавателев",
            requested_organization=organization,
            requested_department=department,
            teacher_registration_code=teacher_code,
            position="Преподаватель",
            employee_code="EMP-001",
        )

        self.assertEqual(user.teacher_profile.requested_organization, organization)
        self.assertEqual(user.teacher_profile.verification_status, VERIFICATION_STATUS_PENDING)

    def test_authenticate_user(self):
        user = self.create_user("auth@example.com")
        result = authenticate_user(email=user.email, password="StrongPass123!")
        self.assertEqual(result.id, user.id)

    def test_verify_user_email_by_token(self):
        user = self.create_user("verify@example.com")
        token = build_verify_email_token(user)

        verify_user_email_by_token(token)
        user.refresh_from_db()

        self.assertTrue(user.is_email_verified)

    def test_reset_password_by_token(self):
        user = self.create_user("reset@example.com")
        token = build_password_reset_token(user)

        reset_password_by_token(
            token=token,
            password="NewStrongPass123!",
            password_repeat="NewStrongPass123!",
        )
        user.refresh_from_db()

        self.assertTrue(user.check_password("NewStrongPass123!"))

    def test_change_user_password(self):
        user = self.create_user("change@example.com")

        change_user_password(
            user=user,
            old_password="StrongPass123!",
            new_password="ChangedStrong123!",
            new_password_confirm="ChangedStrong123!",
        )
        user.refresh_from_db()

        self.assertTrue(user.check_password("ChangedStrong123!"))


class RoleServicesTestCase(BaseUsersServiceTestCase):
    def test_assign_and_remove_role(self):
        user = self.create_user("role-user@example.com")

        assign_role_to_user(user, ROLE_STUDENT)
        self.assertTrue(user_has_role(user, ROLE_STUDENT))

        remove_role_from_user(user, ROLE_STUDENT)
        self.assertFalse(user_has_role(user, ROLE_STUDENT))

    def test_list_user_role_codes(self):
        user = self.create_user("role-list@example.com")
        assign_role_to_user(user, ROLE_STUDENT)

        self.assertIn(ROLE_STUDENT, list_user_role_codes(user))


class ProfileServicesTestCase(BaseUsersServiceTestCase):
    def test_update_base_profile(self):
        user = self.create_user("profile-update@example.com")

        profile = update_base_profile(
            user,
            first_name="Алексей",
            last_name="Обновленный",
            city="Москва",
        )

        self.assertEqual(profile.first_name, "Алексей")
        self.assertEqual(profile.city, "Москва")


class UserServicesTestCase(BaseUsersServiceTestCase):
    def test_mark_user_email_verified(self):
        user = self.create_user("mark@example.com")
        mark_user_email_verified(user)
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

    def test_activate_user_onboarding(self):
        user = self.create_user("activate@example.com")
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        activate_user_onboarding(user, comment="Подтвержден")
        user.refresh_from_db()

        self.assertEqual(user.onboarding_status, ONBOARDING_STATUS_ACTIVE)

    def test_reject_user_onboarding(self):
        user = self.create_user("reject@example.com")
        reject_user_onboarding(user, comment="Недостаточно данных")
        user.refresh_from_db()

        self.assertEqual(user.onboarding_status, ONBOARDING_STATUS_REJECTED)

    def test_block_user(self):
        user = self.create_user("block@example.com")
        block_user(user, comment="Подозрительная активность")
        user.refresh_from_db()

        self.assertFalse(user.is_active)


class StudentServicesTestCase(BaseUsersServiceTestCase):
    def test_submit_student_group_request(self):
        organization, department, group = self.create_org_stack()
        group_code = self.set_group_code(group)

        user = self.create_user("student-service@example.com", registration_type="student")
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        profile = submit_student_group_request(
            student_profile=user.student_profile,
            requested_organization=organization,
            requested_department=department,
            requested_group=group,
            submitted_group_code=group_code,
            student_code="ST-001",
        )

        self.assertEqual(profile.requested_group, group)
        self.assertEqual(profile.verification_status, VERIFICATION_STATUS_PENDING)

    def test_approve_student_profile(self):
        reviewer = self.create_user("reviewer-student@example.com", registration_type="teacher")
        user = self.create_user("student-approve@example.com", registration_type="student")
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        profile = approve_student_profile(
            student_profile=user.student_profile,
            reviewer=reviewer,
            comment="Подтверждено",
        )

        user.refresh_from_db()
        self.assertEqual(profile.verification_status, VERIFICATION_STATUS_APPROVED)
        self.assertEqual(user.onboarding_status, ONBOARDING_STATUS_ACTIVE)
        self.assertTrue(user_has_role(user, ROLE_STUDENT))

    def test_reject_student_profile(self):
        reviewer = self.create_user("reviewer-student-reject@example.com", registration_type="teacher")
        user = self.create_user("student-reject@example.com", registration_type="student")

        profile = reject_student_profile(
            student_profile=user.student_profile,
            reviewer=reviewer,
            comment="Код группы неверен",
        )

        user.refresh_from_db()
        self.assertEqual(profile.verification_status, VERIFICATION_STATUS_REJECTED)
        self.assertEqual(user.onboarding_status, ONBOARDING_STATUS_REJECTED)


class TeacherServicesTestCase(BaseUsersServiceTestCase):
    def test_submit_teacher_verification_request(self):
        organization, department, _ = self.create_org_stack()
        user = self.create_user("teacher-service@example.com", registration_type="teacher")

        profile = submit_teacher_verification_request(
            teacher_profile=user.teacher_profile,
            requested_organization=organization,
            requested_department=department,
            position="Преподаватель информатики",
            employee_code="EMP-001",
        )

        self.assertEqual(profile.requested_organization, organization)
        self.assertEqual(profile.verification_status, VERIFICATION_STATUS_PENDING)

    def test_approve_teacher_profile(self):
        reviewer = self.create_user("reviewer-teacher@example.com", registration_type="teacher")
        user = self.create_user("teacher-approve@example.com", registration_type="teacher")
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        profile = approve_teacher_profile(
            teacher_profile=user.teacher_profile,
            reviewer=reviewer,
            comment="Подтвержден",
        )

        user.refresh_from_db()
        self.assertEqual(profile.verification_status, VERIFICATION_STATUS_APPROVED)
        self.assertEqual(user.onboarding_status, ONBOARDING_STATUS_ACTIVE)
        self.assertTrue(user_has_role(user, ROLE_TEACHER))

    def test_reject_teacher_profile(self):
        reviewer = self.create_user("reviewer-teacher-reject@example.com", registration_type="teacher")
        user = self.create_user("teacher-reject@example.com", registration_type="teacher")

        profile = reject_teacher_profile(
            teacher_profile=user.teacher_profile,
            reviewer=reviewer,
            comment="Недостаточно данных",
        )

        user.refresh_from_db()
        self.assertEqual(profile.verification_status, VERIFICATION_STATUS_REJECTED)
        self.assertEqual(user.onboarding_status, ONBOARDING_STATUS_REJECTED)


class ParentServicesTestCase(BaseUsersServiceTestCase):
    def test_create_parent_student_link_request(self):
        parent = self.create_user("parent-service@example.com", registration_type="parent")
        student = self.create_user("student-service-link@example.com", registration_type="student")

        link = create_parent_student_link_request(
            parent_user=parent,
            student_user=student,
            relation_type=_relation_type_mother(),
            requested_by=parent,
            comment="Мама ученика",
        )

        self.assertEqual(link.status, LINK_STATUS_PENDING)

    def test_approve_parent_student_link(self):
        reviewer = self.create_user("reviewer-parent@example.com", registration_type="teacher")
        parent = self.create_user("parent-approve@example.com", registration_type="parent")
        student = self.create_user("student-approve-link@example.com", registration_type="student")
        parent.is_email_verified = True
        parent.save(update_fields=["is_email_verified"])

        link = create_parent_student_link_request(
            parent_user=parent,
            student_user=student,
            relation_type=ParentStudent.RelationType.FATHER,
            requested_by=parent,
        )

        approve_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment="Подтверждено",
        )

        link.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(link.status, LINK_STATUS_APPROVED)
        self.assertEqual(parent.onboarding_status, ONBOARDING_STATUS_ACTIVE)
        self.assertTrue(user_has_role(parent, ROLE_PARENT))

    def test_reject_parent_student_link(self):
        reviewer = self.create_user("reviewer-parent-reject@example.com", registration_type="teacher")
        parent = self.create_user("parent-reject@example.com", registration_type="parent")
        student = self.create_user("student-reject-link@example.com", registration_type="student")

        link = create_parent_student_link_request(
            parent_user=parent,
            student_user=student,
            relation_type=_relation_type_guardian(),
            requested_by=parent,
        )

        reject_parent_student_link(
            link=link,
            reviewer=reviewer,
            comment="Связь не подтверждена",
        )

        link.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(link.status, "rejected")
        self.assertEqual(parent.onboarding_status, ONBOARDING_STATUS_REJECTED)
