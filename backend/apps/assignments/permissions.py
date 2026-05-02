from __future__ import annotations

from rest_framework.permissions import BasePermission


def _get_user_role_codes(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    if getattr(user, "is_superuser", False):
        return {"admin"}

    if not hasattr(user, "user_roles"):
        return set()

    queryset = user.user_roles.all()
    model_fields = {field.name for field in queryset.model._meta.get_fields()}
    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if getattr(user, "is_superuser", False):
        return True

    return "admin" in _get_user_role_codes(user)


def is_teacher(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if getattr(user, "is_superuser", False):
        return True

    role_codes = _get_user_role_codes(user)
    return "teacher" in role_codes or "admin" in role_codes


def is_student(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    role_codes = _get_user_role_codes(user)
    return "student" in role_codes


class IsAdminOrSuperuser(BasePermission):
    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return is_admin(request.user)


class IsTeacherOrAdmin(BasePermission):
    message = "Доступ разрешён только преподавателю или администратору."

    def has_permission(self, request, view) -> bool:
        return is_teacher(request.user)


class IsAssignmentAuthorOrAdmin(BasePermission):
    message = "Изменять объект может только автор или администратор."

    def has_object_permission(self, request, view, obj) -> bool:
        if is_admin(request.user):
            return True

        author_id = getattr(obj, "author_id", None)
        if author_id is not None:
            return request.user.is_authenticated and author_id == request.user.id

        assignment = getattr(obj, "assignment", None)
        if assignment is not None:
            return (
                request.user.is_authenticated
                and assignment.author_id == request.user.id
            )

        publication = getattr(obj, "publication", None)
        if publication is not None:
            return (
                request.user.is_authenticated
                and publication.assignment.author_id == request.user.id
            )

        return False


class CanManageAssignmentObject(BasePermission):
    message = "У вас нет прав на управление этим объектом."

    def has_permission(self, request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and (is_teacher(request.user) or is_admin(request.user))
        )

    def has_object_permission(self, request, view, obj) -> bool:
        if is_admin(request.user):
            return True

        if hasattr(obj, "author_id"):
            return obj.author_id == request.user.id

        if hasattr(obj, "assignment") and obj.assignment is not None:
            return obj.assignment.author_id == request.user.id

        if hasattr(obj, "publication") and obj.publication is not None:
            return obj.publication.assignment.author_id == request.user.id

        return False


class IsSubmissionOwnerOrReviewerOrAdmin(BasePermission):
    message = "У вас нет доступа к этой сдаче."

    def has_object_permission(self, request, view, obj) -> bool:
        if is_admin(request.user):
            return True

        submission = obj
        if hasattr(obj, "submission"):
            submission = obj.submission

        if not request.user or not request.user.is_authenticated:
            return False

        if getattr(submission, "student_id", None) == request.user.id:
            return True

        assignment = getattr(submission, "assignment", None)
        if (
            assignment is not None
            and getattr(assignment, "author_id", None) == request.user.id
        ):
            return True

        checked_by_id = getattr(submission, "checked_by_id", None)
        if checked_by_id == request.user.id:
            return True

        return False


class IsStudentSubmissionOwner(BasePermission):
    message = "Доступ разрешён только владельцу сдачи."

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        submission = obj
        if hasattr(obj, "submission"):
            submission = obj.submission

        return getattr(submission, "student_id", None) == request.user.id
