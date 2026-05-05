from __future__ import annotations

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission

SCHEDULE_MANAGER_ROLE_CODES = {
    "admin",
    "superadmin",
    "director",
    "deputy_director",
    "methodist",
    "schedule_manager",
}

SCHEDULE_TEACHER_ROLE_CODES = {
    "teacher",
}

SCHEDULE_STUDENT_ROLE_CODES = {
    "student",
}

SCHEDULE_PARENT_ROLE_CODES = {
    "parent",
}


def _get_user_role_codes(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return {"superadmin"}

    role_codes: set[str] = set()

    user_roles = getattr(user, "user_roles", None)
    if user_roles is not None:
        for user_role in user_roles.select_related("role").all():
            role = getattr(user_role, "role", None)
            code = getattr(role, "code", "")
            if code:
                role_codes.add(code)

    return role_codes


def user_can_manage_schedule(user) -> bool:
    role_codes = _get_user_role_codes(user)
    return bool(role_codes & SCHEDULE_MANAGER_ROLE_CODES)


def user_can_view_schedule(user) -> bool:
    role_codes = _get_user_role_codes(user)
    allowed_roles = (
        SCHEDULE_MANAGER_ROLE_CODES
        | SCHEDULE_TEACHER_ROLE_CODES
        | SCHEDULE_STUDENT_ROLE_CODES
        | SCHEDULE_PARENT_ROLE_CODES
    )
    return bool(role_codes & allowed_roles)


def _object_organization_id(obj: Any) -> int | None:
    organization_id = getattr(obj, "organization_id", None)
    if organization_id:
        return organization_id

    group = getattr(obj, "group", None)
    if group is not None:
        return getattr(group, "organization_id", None)

    lesson = getattr(obj, "lesson", None)
    if lesson is not None:
        return getattr(lesson, "organization_id", None)

    scheduled_lesson = getattr(obj, "scheduled_lesson", None)
    if scheduled_lesson is not None:
        return getattr(scheduled_lesson, "organization_id", None)

    pattern = getattr(obj, "pattern", None)
    if pattern is not None:
        return getattr(pattern, "organization_id", None)

    return None


def _user_has_teacher_access_to_object(user, obj: Any) -> bool:
    teacher_id = getattr(obj, "teacher_id", None)
    if teacher_id and teacher_id == user.id:
        return True

    lesson = getattr(obj, "lesson", None)
    if lesson is not None and getattr(lesson, "teacher_id", None) == user.id:
        return True

    scheduled_lesson = getattr(obj, "scheduled_lesson", None)
    if (
        scheduled_lesson is not None
        and getattr(scheduled_lesson, "teacher_id", None) == user.id
    ):
        return True

    pattern = getattr(obj, "pattern", None)
    return pattern is not None and getattr(pattern, "teacher_id", None) == user.id


def _user_has_student_access_to_object(user, obj: Any) -> bool:
    student_profile = getattr(user, "student_profile", None)
    if student_profile is None:
        return False

    student_group_id = getattr(student_profile, "group_id", None)
    if not student_group_id:
        return False

    group_id = getattr(obj, "group_id", None)
    if group_id and group_id == student_group_id:
        return True

    lesson = getattr(obj, "lesson", None)
    if lesson is not None and getattr(lesson, "group_id", None) == student_group_id:
        return True

    scheduled_lesson = getattr(obj, "scheduled_lesson", None)
    if (
        scheduled_lesson is not None
        and getattr(scheduled_lesson, "group_id", None) == student_group_id
    ):
        return True

    pattern = getattr(obj, "pattern", None)
    return (
        pattern is not None and getattr(pattern, "group_id", None) == student_group_id
    )


class IsScheduleManager(BasePermission):
    message = "Недостаточно прав для управления расписанием."

    def has_permission(self, request, view) -> bool:
        return user_can_manage_schedule(request.user)


class CanViewSchedule(BasePermission):
    message = "Недостаточно прав для просмотра расписания."

    def has_permission(self, request, view) -> bool:
        return user_can_view_schedule(request.user)


class CanManageScheduleOrReadOnly(BasePermission):
    message = "Недостаточно прав для изменения расписания."

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return user_can_view_schedule(request.user)

        return user_can_manage_schedule(request.user)


class ScheduleObjectPermission(BasePermission):
    message = "Недостаточно прав для доступа к объекту расписания."

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return user_can_view_schedule(request.user)

        return user_can_manage_schedule(request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user

        if user_can_manage_schedule(user):
            return True

        if request.method not in SAFE_METHODS:
            return False

        if _user_has_teacher_access_to_object(user, obj):
            return True

        return _user_has_student_access_to_object(user, obj)


class CanResolveScheduleConflict(BasePermission):
    message = "Недостаточно прав для разрешения конфликтов расписания."

    def has_permission(self, request, view) -> bool:
        return user_can_manage_schedule(request.user)


class CanImportExportSchedule(BasePermission):
    message = "Недостаточно прав для импорта или экспорта расписания."

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return user_can_view_schedule(request.user)

        return user_can_manage_schedule(request.user)


class CanPublishSchedule(BasePermission):
    message = "Недостаточно прав для публикации расписания."

    def has_permission(self, request, view) -> bool:
        return user_can_manage_schedule(request.user)
