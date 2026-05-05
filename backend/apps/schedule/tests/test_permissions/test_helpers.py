from __future__ import annotations

from django.test import SimpleTestCase

from apps.schedule.permissions import (
    user_can_manage_schedule,
    user_can_view_schedule,
)

from .fakes import make_user


class SchedulePermissionHelpersTestCase(SimpleTestCase):
    def test_staff_or_superuser_can_manage_schedule(self):
        staff_user = make_user(is_staff=True)
        superuser = make_user(is_superuser=True)

        self.assertTrue(user_can_manage_schedule(staff_user))
        self.assertTrue(user_can_manage_schedule(superuser))

    def test_manager_roles_can_manage_schedule(self):
        manager_role_codes = (
            "admin",
            "superadmin",
            "director",
            "deputy_director",
            "methodist",
            "schedule_manager",
        )

        for role_code in manager_role_codes:
            with self.subTest(role_code=role_code):
                user = make_user(role_codes=(role_code,))

                self.assertTrue(user_can_manage_schedule(user))

    def test_non_manager_roles_cannot_manage_schedule(self):
        for role_code in ("teacher", "student", "parent", "unknown"):
            with self.subTest(role_code=role_code):
                user = make_user(role_codes=(role_code,))

                self.assertFalse(user_can_manage_schedule(user))

    def test_view_roles_can_view_schedule(self):
        allowed_role_codes = (
            "admin",
            "superadmin",
            "director",
            "deputy_director",
            "methodist",
            "schedule_manager",
            "teacher",
            "student",
            "parent",
        )

        for role_code in allowed_role_codes:
            with self.subTest(role_code=role_code):
                user = make_user(role_codes=(role_code,))

                self.assertTrue(user_can_view_schedule(user))

    def test_anonymous_or_unknown_role_cannot_view_schedule(self):
        anonymous_user = make_user(is_authenticated=False)
        unknown_role_user = make_user(role_codes=("unknown",))

        self.assertFalse(user_can_view_schedule(anonymous_user))
        self.assertFalse(user_can_view_schedule(unknown_role_user))
