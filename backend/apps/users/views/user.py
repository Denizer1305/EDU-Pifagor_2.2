from __future__ import annotations

import logging

from rest_framework import generics, permissions

from apps.users.filters import UserFilter
from apps.users.permissions import CanManageUserRoles
from apps.users.selectors.user_selectors import get_users_queryset
from apps.users.serializers import UserDetailSerializer, UserListSerializer, UserUpdateSerializer


logger = logging.getLogger(__name__)

class UserListView(generics.ListAPIView):
    """Представление API для user list."""
    permission_classes = [CanManageUserRoles]
    serializer_class = UserListSerializer
    filterset_class = UserFilter
    search_fields = (
        "email", "profile__first_name",
        "profile__last_name",
    )
    ordering_fields = (
        "created_at", "email",
    )

    def get_queryset(self):
        """Возвращает queryset для текущего запроса."""
        logger.info("UserListView.get_queryset called")
        return get_users_queryset()


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Представление API для user detail."""
    permission_classes = [CanManageUserRoles]

    def get_queryset(self):
        """Возвращает queryset для текущего запроса."""
        logger.info("UserDetailView.get_queryset called")
        return get_users_queryset()

    def get_serializer_class(self):
        """Возвращает класс сериализатора для текущего действия."""
        logger.info("UserDetailView.get_serializer_class called")
        if self.request.method in permissions.SAFE_METHODS:
            return UserDetailSerializer
        return UserUpdateSerializer
