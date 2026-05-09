from __future__ import annotations

from django.contrib.auth import get_user_model, login, logout
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.users.serializers.auth import LoginSerializer
from apps.users.serializers.user import CurrentUserSerializer

User = get_user_model()


class LoginAPIView(APIView):
    """Вход пользователя в систему."""

    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth_login"

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if user.onboarding_status == User.OnboardingStatusChoices.BLOCKED:
            raise ValidationError({"detail": _("Учетная запись заблокирована.")})

        login(request, user)

        data = CurrentUserSerializer(
            user,
            context={"request": request},
        ).data
        return Response(data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """Выход пользователя из системы."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"detail": _("Вы успешно вышли из системы.")},
            status=status.HTTP_200_OK,
        )
