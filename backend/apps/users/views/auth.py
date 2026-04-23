from __future__ import annotations

import logging
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth import (
    ChangePasswordSerializer,
    LoginSerializer,
    ParentRegistrationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
)
from apps.users.serializers.user import CurrentUserSerializer
from apps.users.services.auth_services import (
    build_password_reset_token,
    build_verify_email_token,
    change_user_password,
    reset_password_by_token,
    verify_user_email_by_token,
)
from apps.users.tasks import (
    send_password_changed_email_task,
    send_reset_password_email_task,
    send_verify_email_task,
    send_welcome_email_task,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _get_frontend_url(path: str, token: str) -> str:
    base_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{base_url}{path}?{urlencode({'token': token})}"


def _safe_delay(task, *args) -> None:
    try:
        task.delay(*args)
    except Exception:  # pragma: no cover
        logger.exception(
            "Не удалось поставить Celery-задачу %s в очередь.",
            getattr(task, "__name__", task),
        )


def _get_register_serializer_class(registration_type: str):
    registration_type = (registration_type or "").strip().lower()

    mapping = {
        User.RegistrationTypeChoices.STUDENT: StudentRegistrationSerializer,
        User.RegistrationTypeChoices.PARENT: ParentRegistrationSerializer,
        User.RegistrationTypeChoices.TEACHER: TeacherRegistrationSerializer,
    }
    serializer_class = mapping.get(registration_type)

    if serializer_class is None:
        raise ValidationError(
            {
                "registration_type": _(
                    "Допустимые значения: student, parent, teacher."
                )
            }
        )

    return serializer_class


class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer_class = _get_register_serializer_class(
            request.data.get("registration_type", "")
        )
        serializer = serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        verify_expiry_seconds = int(
            getattr(settings, "VERIFY_EMAIL_TOKEN_TTL", 60 * 60 * 24)
        )
        verify_token = build_verify_email_token(user)
        verify_url = _get_frontend_url(
            getattr(settings, "FRONTEND_VERIFY_EMAIL_PATH", "/verify-email"),
            verify_token,
        )
        expires_at = (
            timezone.now() + timedelta(seconds=verify_expiry_seconds)
        ).strftime("%d.%m.%Y %H:%M")

        _safe_delay(send_verify_email_task, user.id, verify_url, expires_at)

        data = CurrentUserSerializer(user, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if user.onboarding_status == User.OnboardingStatusChoices.BLOCKED:
            raise ValidationError(
                {"detail": _("Учетная запись заблокирована.")}
            )

        login(request, user)

        data = CurrentUserSerializer(user, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"detail": _("Вы успешно вышли из системы.")},
            status=status.HTTP_200_OK,
        )


class VerifyEmailAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        token = (
            request.data.get("token")
            or request.query_params.get("token")
            or ""
        ).strip()

        if not token:
            raise ValidationError({"token": _("Не передан токен подтверждения.")})

        user = verify_user_email_by_token(token)
        _safe_delay(send_welcome_email_task, user.id)

        return Response(
            {"detail": _("Электронная почта успешно подтверждена.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email=email,
            is_active=True,
        ).first()

        if user:
            max_age = int(getattr(settings, "RESET_PASSWORD_TOKEN_TTL", 60 * 60 * 3))
            reset_token = build_password_reset_token(user)
            reset_url = _get_frontend_url(
                getattr(settings, "FRONTEND_RESET_PASSWORD_PATH", "/reset-password"),
                reset_token,
            )
            expires_at = (
                timezone.now() + timedelta(seconds=max_age)
            ).strftime("%d.%m.%Y %H:%M")

            _safe_delay(send_reset_password_email_task, user.id, reset_url, expires_at)

        return Response(
            {
                "detail": _(
                    "Если пользователь с такой почтой существует, инструкция по восстановлению будет отправлена."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        token = (
            request.data.get("token")
            or request.query_params.get("token")
            or ""
        ).strip()

        if not token:
            raise ValidationError({"token": _("Не передан токен восстановления.")})

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = reset_password_by_token(
            token=token,
            password=serializer.validated_data["password"],
            password_repeat=serializer.validated_data["password_repeat"],
        )

        _safe_delay(send_password_changed_email_task, user.id)

        return Response(
            {"detail": _("Пароль успешно обновлён.")},
            status=status.HTTP_200_OK,
        )


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = change_user_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
            new_password_confirm=serializer.validated_data["new_password_confirm"],
        )

        update_session_auth_hash(request, user)
        _safe_delay(send_password_changed_email_task, user.id)

        return Response(
            {"detail": _("Пароль успешно изменён.")},
            status=status.HTTP_200_OK,
        )
