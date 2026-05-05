from __future__ import annotations

from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.schedule.permissions import ScheduleObjectPermission

from .fakes import make_request, make_user


class ScheduleObjectPermissionTestCase(SimpleTestCase):
    def test_manager_has_object_permission_for_safe_and_write_methods(self):
        permission = ScheduleObjectPermission()
        manager = make_user(role_codes=("schedule_manager",))
        schedule_object = SimpleNamespace(organization_id=1)

        get_request = make_request("GET", manager)
        patch_request = make_request("PATCH", manager)

        self.assertTrue(
            permission.has_object_permission(
                get_request,
                view=None,
                obj=schedule_object,
            )
        )
        self.assertTrue(
            permission.has_object_permission(
                patch_request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_non_manager_write_object_permission_is_denied(self):
        permission = ScheduleObjectPermission()
        teacher = make_user(user_id=10, role_codes=("teacher",))
        schedule_object = SimpleNamespace(teacher_id=10)

        patch_request = make_request("PATCH", teacher)

        self.assertFalse(
            permission.has_object_permission(
                patch_request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_teacher_can_read_object_where_teacher_id_matches(self):
        permission = ScheduleObjectPermission()
        teacher = make_user(user_id=10, role_codes=("teacher",))
        schedule_object = SimpleNamespace(teacher_id=10)

        request = make_request("GET", teacher)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_teacher_can_read_object_through_lesson_relation(self):
        permission = ScheduleObjectPermission()
        teacher = make_user(user_id=10, role_codes=("teacher",))
        schedule_object = SimpleNamespace(
            lesson=SimpleNamespace(teacher_id=10),
        )

        request = make_request("GET", teacher)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_teacher_can_read_object_through_scheduled_lesson_relation(self):
        permission = ScheduleObjectPermission()
        teacher = make_user(user_id=10, role_codes=("teacher",))
        schedule_object = SimpleNamespace(
            scheduled_lesson=SimpleNamespace(teacher_id=10),
        )

        request = make_request("GET", teacher)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_teacher_can_read_object_through_pattern_relation(self):
        permission = ScheduleObjectPermission()
        teacher = make_user(user_id=10, role_codes=("teacher",))
        schedule_object = SimpleNamespace(
            pattern=SimpleNamespace(teacher_id=10),
        )

        request = make_request("GET", teacher)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_teacher_cannot_read_unrelated_object(self):
        permission = ScheduleObjectPermission()
        teacher = make_user(user_id=10, role_codes=("teacher",))
        schedule_object = SimpleNamespace(teacher_id=99)

        request = make_request("GET", teacher)

        self.assertFalse(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_student_can_read_object_where_group_id_matches(self):
        permission = ScheduleObjectPermission()
        student = make_user(
            user_id=20,
            role_codes=("student",),
            student_group_id=5,
        )
        schedule_object = SimpleNamespace(group_id=5)

        request = make_request("GET", student)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_student_can_read_object_through_lesson_relation(self):
        permission = ScheduleObjectPermission()
        student = make_user(
            user_id=20,
            role_codes=("student",),
            student_group_id=5,
        )
        schedule_object = SimpleNamespace(
            lesson=SimpleNamespace(group_id=5),
        )

        request = make_request("GET", student)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_student_can_read_object_through_scheduled_lesson_relation(self):
        permission = ScheduleObjectPermission()
        student = make_user(
            user_id=20,
            role_codes=("student",),
            student_group_id=5,
        )
        schedule_object = SimpleNamespace(
            scheduled_lesson=SimpleNamespace(group_id=5),
        )

        request = make_request("GET", student)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_student_can_read_object_through_pattern_relation(self):
        permission = ScheduleObjectPermission()
        student = make_user(
            user_id=20,
            role_codes=("student",),
            student_group_id=5,
        )
        schedule_object = SimpleNamespace(
            pattern=SimpleNamespace(group_id=5),
        )

        request = make_request("GET", student)

        self.assertTrue(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_student_cannot_read_object_from_another_group(self):
        permission = ScheduleObjectPermission()
        student = make_user(
            user_id=20,
            role_codes=("student",),
            student_group_id=5,
        )
        schedule_object = SimpleNamespace(group_id=99)

        request = make_request("GET", student)

        self.assertFalse(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )

    def test_student_without_profile_cannot_read_group_object(self):
        permission = ScheduleObjectPermission()
        student = make_user(
            user_id=20,
            role_codes=("student",),
        )
        schedule_object = SimpleNamespace(group_id=5)

        request = make_request("GET", student)

        self.assertFalse(
            permission.has_object_permission(
                request,
                view=None,
                obj=schedule_object,
            )
        )
