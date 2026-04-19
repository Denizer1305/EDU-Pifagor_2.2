from __future__ import annotations

import logging

from rest_framework import generics, permissions

from apps.users.serializers import StudentProfileDetailSerializer, StudentProfileUpdateSerializer


logger = logging.getLogger(__name__)

class MyStudentProfileView(generics.RetrieveUpdateAPIView):
    """Представление API для my student profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает объект для текущего пользователя."""
        logger.info("MyStudentProfileView.get_object called")
        return self.request.user.student_profile

    def get_serializer_class(self):
        """Возвращает класс сериализатора для текущего действия."""
        logger.info("MyStudentProfileView.get_serializer_class called")
        if self.request.method in permissions.SAFE_METHODS:
            return StudentProfileDetailSerializer
        return StudentProfileUpdateSerializer
