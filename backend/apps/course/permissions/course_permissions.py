from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.course.models import Course
from apps.course.permissions.access import (
    _is_active_course_teacher,
    _is_course_owner,
)
from apps.course.permissions.object_utils import (
    _get_course_from_obj,
    _get_student_from_obj,
)
from apps.course.permissions.roles import is_admin_user


class IsCourseTeacherOrAdmin(BasePermission):
    message = "У вас нет прав на управление этим курсом."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        course = _get_course_from_obj(obj)
        return _is_active_course_teacher(user, course)


class IsCourseOwnerOrAdmin(BasePermission):
    message = "Только владелец курса или администратор может выполнить это действие."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        course = _get_course_from_obj(obj)
        return _is_course_owner(user, course)


class IsEnrolledStudentOrTeacherOrAdmin(BasePermission):
    message = "У вас нет прав для доступа к данным курса."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        course = _get_course_from_obj(obj)
        if course is not None and _is_active_course_teacher(user, course):
            return True

        student = _get_student_from_obj(obj)
        if student is not None and student == user:
            return True

        if isinstance(obj, Course):
            return obj.enrollments.filter(student=user).exists()

        return False


class IsPublishedCourseVisible(BasePermission):
    message = "Курс недоступен для просмотра."

    def has_object_permission(self, request, view, obj) -> bool:
        course = _get_course_from_obj(obj)
        user = request.user

        if course is None:
            return False

        if course.status != Course.StatusChoices.PUBLISHED or not course.is_active:
            return False

        if course.visibility == Course.VisibilityChoices.PUBLIC_LINK:
            return True

        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        if _is_active_course_teacher(user, course):
            return True

        if course.visibility == Course.VisibilityChoices.ORGANIZATION:
            if not course.organization_id:
                return True

            teacher_profile = getattr(user, "teacher_profile", None)
            if (
                teacher_profile
                and getattr(teacher_profile, "requested_organization_id", None)
                == course.organization_id
            ):
                return True

            student_profile = getattr(user, "student_profile", None)
            if (
                student_profile
                and getattr(student_profile, "requested_organization_id", None)
                == course.organization_id
            ):
                return True

        if course.visibility == Course.VisibilityChoices.ASSIGNED_ONLY:
            return course.enrollments.filter(student=user).exists()

        if course.visibility == Course.VisibilityChoices.PRIVATE:
            return course.author_id == user.id or _is_active_course_teacher(
                user, course
            )

        return False
