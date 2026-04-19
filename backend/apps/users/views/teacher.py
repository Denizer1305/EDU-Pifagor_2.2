from __future__ import annotations

import logging

from rest_framework import generics, permissions

from apps.users.filters import TeacherProfileFilter
from apps.users.permissions import IsTeacherProfileOwnerOrAdmin
from apps.users.selectors.teacher_selectors import (
    get_public_teacher_profiles_queryset,
    get_teacher_profiles_queryset,
)
from apps.users.serializers import (
    TeacherProfileDetailSerializer,
    TeacherProfileListSerializer,
    TeacherProfileUpdateSerializer,
)


logger = logging.getLogger(__name__)

class TeacherPublicListView(generics.ListAPIView):
    """Представление API для teacher public list."""
    permission_classes = [permissions.AllowAny]
    serializer_class = TeacherProfileListSerializer
    filterset_class = TeacherProfileFilter

    def get_queryset(self):
        """Возвращает queryset для текущего запроса."""
        logger.info("TeacherPublicListView.get_queryset called")
        return get_public_teacher_profiles_queryset()


class TeacherProfileDetailView(generics.RetrieveAPIView):
    """Представление API для teacher profile detail."""
    permission_classes = [permissions.AllowAny]
    serializer_class = TeacherProfileDetailSerializer

    def get_queryset(self):
        """Возвращает queryset для текущего запроса."""
        logger.info("TeacherProfileDetailView.get_queryset called")
        return get_public_teacher_profiles_queryset()


class MyTeacherProfileView(generics.RetrieveUpdateAPIView):
    """Представление API для my teacher profile."""
    permission_classes = [permissions.IsAuthenticated, IsTeacherProfileOwnerOrAdmin]

    def get_object(self):
        """Возвращает объект для текущего пользователя."""
        logger.info("MyTeacherProfileView.get_object called")
        return self.request.user.teacher_profile

    def get_serializer_class(self):
        """Возвращает класс сериализатора для текущего действия."""
        logger.info("MyTeacherProfileView.get_serializer_class called")
        if self.request.method in permissions.SAFE_METHODS:
            return TeacherProfileDetailSerializer
        return TeacherProfileUpdateSerializer
