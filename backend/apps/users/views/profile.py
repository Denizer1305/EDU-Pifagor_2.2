from __future__ import annotations

import logging

from rest_framework import generics, permissions

from apps.users.selectors.profile_selectors import get_profiles_queryset
from apps.users.serializers import ProfileDetailSerializer, ProfileUpdateSerializer


logger = logging.getLogger(__name__)

class MyProfileView(generics.RetrieveUpdateAPIView):
    """Представление API для my profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает объект для текущего пользователя."""
        logger.info("MyProfileView.get_object called")
        return self.request.user.profile

    def get_serializer_class(self):
        """Возвращает класс сериализатора для текущего действия."""
        logger.info("MyProfileView.get_serializer_class called")
        if self.request.method in permissions.SAFE_METHODS:
            return ProfileDetailSerializer
        return ProfileUpdateSerializer


class ProfileDetailView(generics.RetrieveAPIView):
    """Представление API для profile detail."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileDetailSerializer

    def get_queryset(self):
        """Возвращает queryset для текущего запроса."""
        logger.info("ProfileDetailView.get_queryset called")
        return get_profiles_queryset()
