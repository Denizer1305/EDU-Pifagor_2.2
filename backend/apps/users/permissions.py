from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.constants import ROLE_ADMIN


def _get_user_role_codes(user) -> set[str]:
    """
    Возвращает множество кодов ролей пользователя.

    Поддерживает оба сценария:
    - у UserRole есть поле is_active
    - у UserRole нет поля is_active
    """
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_ADMIN}

    if not hasattr(user, "user_roles"):
        return set()

    queryset = user.user_roles.all()

    user_role_model = queryset.model
    model_fields = {field.name for field in user_role_model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def _is_admin_user(user) -> bool:
    """
    Проверяет, является ли пользователь администратором платформы.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    role_codes = _get_user_role_codes(user)
    return ROLE_ADMIN in role_codes


class IsSelfOrAdmin(BasePermission):
    """
    Доступ владельцу объекта или администратору.
    Объект может быть:
    - User
    - моделью с полем user
    """

    message = "У вас нет прав на доступ к этому объекту."

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if _is_admin_user(user):
            return True

        target_user = getattr(obj, "user", obj)
        return target_user == user


class CanManageUserRoles(BasePermission):
    """
    Управлять пользователями и ролями могут:
    - superuser
    - пользователь с бизнес-ролью admin
    """

    message = "У вас нет прав на управление пользователями и ролями."

    def has_permission(self, request, view) -> bool:
        return _is_admin_user(request.user)


class IsReadOnlyOrAdmin(BasePermission):
    """
    Чтение доступно авторизованным пользователям.
    Изменение доступно только администраторам.
    """

    message = "Изменение доступно только администраторам."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return _is_admin_user(user)


class IsTeacherProfileOwnerOrAdmin(BasePermission):
    """
    Доступ к teacher_profile:
    - владельцу teacher_profile
    - superuser
    - пользователю с ролью admin
    """

    message = "У вас нет прав на управление профилем преподавателя."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if _is_admin_user(user):
            return True

        return getattr(obj, "user_id", None) == user.id


class IsStudentProfileOwnerOrAdmin(BasePermission):
    """
    Доступ к student_profile:
    - владельцу student_profile
    - superuser
    - пользователю с ролью admin
    """

    message = "У вас нет прав на управление профилем студента."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if _is_admin_user(user):
            return True

        return getattr(obj, "user_id", None) == user.id


class IsParentProfileOwnerOrAdmin(BasePermission):
    """
    Доступ к parent_profile:
    - владельцу parent_profile
    - superuser
    - пользователю с ролью admin
    """

    message = "У вас нет прав на управление профилем родителя."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if _is_admin_user(user):
            return True

        return getattr(obj, "user_id", None) == user.id


class CanReviewStudentVerification(BasePermission):
    """
    Подтверждать учебную привязку студента могут:
    - superuser
    - пользователь с ролью admin
    - активный куратор запрошенной группы
    """

    message = "У вас нет прав на подтверждение учебной привязки студента."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if _is_admin_user(user):
            return True

        requested_group = getattr(obj, "requested_group", None)
        if requested_group is None:
            return False

        from apps.organizations.models import GroupCurator

        queryset = GroupCurator.objects.filter(
            teacher=user,
            group=requested_group,
        )

        model_fields = {field.name for field in GroupCurator._meta.get_fields()}
        if "is_active" in model_fields:
            queryset = queryset.filter(is_active=True)

        return queryset.exists()


class CanReviewTeacherVerification(BasePermission):
    """
    Подтверждать преподавательский профиль могут:
    - superuser
    - пользователь с ролью admin
    """

    message = "У вас нет прав на подтверждение преподавательского профиля."

    def has_permission(self, request, view) -> bool:
        return _is_admin_user(request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class CanReviewParentStudentLink(BasePermission):
    """
    Подтверждать связь родителя и студента могут:
    - superuser
    - пользователь с ролью admin
    """

    message = "У вас нет прав на подтверждение связи родителя и студента."

    def has_permission(self, request, view) -> bool:
        return _is_admin_user(request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)
