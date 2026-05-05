from __future__ import annotations

from django.test import SimpleTestCase

from apps.schedule.permissions import (
    CanImportExportSchedule,
    CanPublishSchedule,
    CanResolveScheduleConflict,
)

from .fakes import make_request, make_user


class SpecialSchedulePermissionClassesTestCase(SimpleTestCase):
    def test_can_resolve_schedule_conflict_allows_only_manager(self):
        permission = CanResolveScheduleConflict()

        manager_request = make_request(
            "POST",
            make_user(role_codes=("schedule_manager",)),
        )
        teacher_request = make_request(
            "POST",
            make_user(role_codes=("teacher",)),
        )

        self.assertTrue(permission.has_permission(manager_request, view=None))
        self.assertFalse(permission.has_permission(teacher_request, view=None))

    def test_can_import_export_schedule_allows_safe_methods_for_viewers(self):
        permission = CanImportExportSchedule()

        teacher_request = make_request(
            "GET",
            make_user(role_codes=("teacher",)),
        )
        student_request = make_request(
            "GET",
            make_user(role_codes=("student",)),
        )

        self.assertTrue(permission.has_permission(teacher_request, view=None))
        self.assertTrue(permission.has_permission(student_request, view=None))

    def test_can_import_export_schedule_allows_write_only_for_manager(self):
        permission = CanImportExportSchedule()

        manager_request = make_request(
            "POST",
            make_user(role_codes=("schedule_manager",)),
        )
        teacher_request = make_request(
            "POST",
            make_user(role_codes=("teacher",)),
        )

        self.assertTrue(permission.has_permission(manager_request, view=None))
        self.assertFalse(permission.has_permission(teacher_request, view=None))

    def test_can_publish_schedule_allows_only_manager(self):
        permission = CanPublishSchedule()

        manager_request = make_request(
            "POST",
            make_user(role_codes=("schedule_manager",)),
        )
        teacher_request = make_request(
            "POST",
            make_user(role_codes=("teacher",)),
        )

        self.assertTrue(permission.has_permission(manager_request, view=None))
        self.assertFalse(permission.has_permission(teacher_request, view=None))
