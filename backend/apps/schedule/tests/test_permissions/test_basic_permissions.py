from __future__ import annotations

from django.test import SimpleTestCase

from apps.schedule.permissions import (
    CanManageScheduleOrReadOnly,
    CanViewSchedule,
    IsScheduleManager,
)

from .fakes import make_request, make_user


class BasicSchedulePermissionClassesTestCase(SimpleTestCase):
    def test_is_schedule_manager_allows_only_manager(self):
        permission = IsScheduleManager()

        manager_request = make_request(
            "GET",
            make_user(role_codes=("schedule_manager",)),
        )
        teacher_request = make_request(
            "GET",
            make_user(role_codes=("teacher",)),
        )

        self.assertTrue(permission.has_permission(manager_request, view=None))
        self.assertFalse(permission.has_permission(teacher_request, view=None))

    def test_can_view_schedule_allows_view_roles(self):
        permission = CanViewSchedule()

        teacher_request = make_request("GET", make_user(role_codes=("teacher",)))
        student_request = make_request("GET", make_user(role_codes=("student",)))
        unknown_request = make_request("GET", make_user(role_codes=("unknown",)))

        self.assertTrue(permission.has_permission(teacher_request, view=None))
        self.assertTrue(permission.has_permission(student_request, view=None))
        self.assertFalse(permission.has_permission(unknown_request, view=None))

    def test_can_manage_schedule_or_read_only_allows_safe_methods_for_viewers(self):
        permission = CanManageScheduleOrReadOnly()
        teacher = make_user(role_codes=("teacher",))

        get_request = make_request("GET", teacher)
        head_request = make_request("HEAD", teacher)
        options_request = make_request("OPTIONS", teacher)

        self.assertTrue(permission.has_permission(get_request, view=None))
        self.assertTrue(permission.has_permission(head_request, view=None))
        self.assertTrue(permission.has_permission(options_request, view=None))

    def test_can_manage_schedule_or_read_only_denies_write_for_non_manager(self):
        permission = CanManageScheduleOrReadOnly()
        teacher = make_user(role_codes=("teacher",))

        post_request = make_request("POST", teacher)
        patch_request = make_request("PATCH", teacher)
        delete_request = make_request("DELETE", teacher)

        self.assertFalse(permission.has_permission(post_request, view=None))
        self.assertFalse(permission.has_permission(patch_request, view=None))
        self.assertFalse(permission.has_permission(delete_request, view=None))

    def test_can_manage_schedule_or_read_only_allows_write_for_manager(self):
        permission = CanManageScheduleOrReadOnly()
        manager = make_user(role_codes=("schedule_manager",))

        post_request = make_request("POST", manager)
        patch_request = make_request("PATCH", manager)
        delete_request = make_request("DELETE", manager)

        self.assertTrue(permission.has_permission(post_request, view=None))
        self.assertTrue(permission.has_permission(patch_request, view=None))
        self.assertTrue(permission.has_permission(delete_request, view=None))
