from __future__ import annotations

import logging

from rest_framework import generics, permissions

from apps.users.permissions import IsParentProfileOwnerOrAdmin
from apps.users.selectors.parent_selectors import get_parent_student_links_queryset
from apps.users.serializers import (
    ParentProfileDetailSerializer,
    ParentProfileUpdateSerializer,
    ParentStudentSerializer,
)


logger = logging.getLogger(__name__)

class MyParentProfileView(generics.RetrieveUpdateAPIView):
    """Представление API для my parent profile."""
    permission_classes = [permissions.IsAuthenticated, IsParentProfileOwnerOrAdmin]

    def get_object(self):
        """Возвращает объект для текущего пользователя."""
        logger.info("MyParentProfileView.get_object called")
        return self.request.user.parent_profile

    def get_serializer_class(self):
        """Возвращает класс сериализатора для текущего действия."""
        logger.info("MyParentProfileView.get_serializer_class called")
        if self.request.method in permissions.SAFE_METHODS:
            return ParentProfileDetailSerializer
        return ParentProfileUpdateSerializer


class MyChildrenListView(generics.ListAPIView):
    """Представление API для my children list."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ParentStudentSerializer

    def get_queryset(self):
        """Возвращает queryset для текущего запроса."""
        logger.info("MyChildrenListView.get_queryset called")
        return get_parent_student_links_queryset().filter(parent=self.request.user)
