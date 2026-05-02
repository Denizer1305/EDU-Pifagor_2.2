from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.course.models import Course
from apps.users.constants import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER


def _get_user_role_codes(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_ADMIN}

    if not hasattr(user, "user_roles"):
        return set()

    queryset = user.user_roles.all()
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def is_admin_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


def is_teacher_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    role_codes = _get_user_role_codes(user)
    return (
        ROLE_TEACHER in role_codes
        or getattr(user, "registration_type", "") == "teacher"
    )


def is_student_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    role_codes = _get_user_role_codes(user)
    return (
        ROLE_STUDENT in role_codes
        or getattr(user, "registration_type", "") == "student"
    )


def _get_course_from_obj(obj):
    if obj is None:
        return None

    if isinstance(obj, Course):
        return obj

    course = getattr(obj, "course", None)
    if course is not None:
        return course

    module = getattr(obj, "module", None)
    if module is not None and getattr(module, "course", None) is not None:
        return module.course

    lesson = getattr(obj, "lesson", None)
    if lesson is not None and getattr(lesson, "course", None) is not None:
        return lesson.course

    enrollment = getattr(obj, "enrollment", None)
    if enrollment is not None and getattr(enrollment, "course", None) is not None:
        return enrollment.course

    course_progress = getattr(obj, "course_progress", None)
    if course_progress is not None:
        enrollment = getattr(course_progress, "enrollment", None)
        if enrollment is not None and getattr(enrollment, "course", None) is not None:
            return enrollment.course

    assignment = getattr(obj, "assignment", None)
    if assignment is not None and getattr(assignment, "course", None) is not None:
        return assignment.course

    return None


def _get_student_from_obj(obj):
    if obj is None:
        return None

    student = getattr(obj, "student", None)
    if student is not None:
        return student

    enrollment = getattr(obj, "enrollment", None)
    if enrollment is not None and getattr(enrollment, "student", None) is not None:
        return enrollment.student

    course_progress = getattr(obj, "course_progress", None)
    if course_progress is not None:
        enrollment = getattr(course_progress, "enrollment", None)
        if enrollment is not None and getattr(enrollment, "student", None) is not None:
            return enrollment.student

    return None


def _is_active_course_teacher(user, course: Course) -> bool:
    if not user or not user.is_authenticated or course is None:
        return False

    if is_admin_user(user):
        return True

    return course.course_teachers.filter(
        teacher=user,
        is_active=True,
    ).exists()


def _is_course_owner(user, course: Course) -> bool:
    if not user or not user.is_authenticated or course is None:
        return False

    if is_admin_user(user):
        return True

    return course.course_teachers.filter(
        teacher=user,
        is_active=True,
        role="owner",
    ).exists()


class IsAdminOnly(BasePermission):
    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return is_admin_user(request.user)


class IsTeacherOrAdmin(BasePermission):
    message = "Действие доступно только преподавателю или администратору."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (is_teacher_user(user) or is_admin_user(user))
        )


class IsTeacherOrAdminReadOnly(BasePermission):
    message = "У вас нет прав для доступа к этому разделу."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return is_teacher_user(user) or is_admin_user(user)

        return is_teacher_user(user) or is_admin_user(user)


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
