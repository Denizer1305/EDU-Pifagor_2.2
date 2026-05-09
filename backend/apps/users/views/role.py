from __future__ import annotations

from rest_framework import viewsets

from apps.users.filters import RoleFilter, UserRoleFilter
from apps.users.models import Role, UserRole
from apps.users.permissions import CanManageUserRoles
from apps.users.serializers.role import RoleSerializer, UserRoleSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (CanManageUserRoles,)
    filterset_class = RoleFilter
    ordering_fields = (
        "name",
        "code",
        "created_at",
        "updated_at",
    )
    ordering = (
        "name",
        "code",
    )


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.select_related(
        "user",
        "user__profile",
        "role",
    )
    serializer_class = UserRoleSerializer
    permission_classes = (CanManageUserRoles,)
    filterset_class = UserRoleFilter
    ordering_fields = (
        "assigned_at",
        "created_at",
        "updated_at",
    )
    ordering = (
        "-assigned_at",
        "-created_at",
    )
