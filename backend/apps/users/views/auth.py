from __future__ import annotations

import logging

from django.contrib.auth import login, logout
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import (
    ChangePasswordSerializer,
    CurrentUserSerializer,
    LoginSerializer,
    RegisterSerializer,
)
from apps.users.services.auth_services import change_user_password, register_user

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """Представление API для login."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Обрабатывает POST-запрос."""
        logger.info("login requested")
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)
        logger.info("login success user_id=%s", user.id)

        return Response(CurrentUserSerializer(user).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Представление API для logout."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Обрабатывает POST-запрос."""
        logger.info("logout user_id=%s", request.user.id)
        logout(request)
        return Response({"detail": "Выход выполнен успешно."}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """Представление API для register."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Обрабатывает POST-запрос."""
        logger.info("register requested")
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            patronymic=serializer.validated_data.get("patronymic", ""),
            phone=serializer.validated_data["phone"],
        )
        logger.info("register success user_id=%s", user.id)
        return Response(CurrentUserSerializer(user).data, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    """Представление API для current user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Обрабатывает GET-запрос."""
        logger.info("CurrentUserView.get called")
        return Response(CurrentUserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """Представление API для change password."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Обрабатывает POST-запрос."""
        logger.info("change_password requested user_id=%s", request.user.id)
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        change_user_password(
            user=request.user,
            new_password=serializer.validated_data["new_password"],
        )
        logger.info("change_password success user_id=%s", request.user.id)
        return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
