from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)
from apps.users.services.auth_services import (
    build_password_reset_token,
    change_user_password,
    reset_password_by_token,
)
from apps.users.tasks import (
    send_password_changed_email_task,
    send_reset_password_email_task,
)
from apps.users.views.auth.helpers import (
    get_frontend_url,
    safe_delay,
)

User = get_user_model()


class PasswordResetRequestAPIView(APIView):
    """Запрос восстановления пароля."""

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
            reset_url = get_frontend_url(
                getattr(
                    settings,
                    "FRONTEND_RESET_PASSWORD_PATH",
                    "/reset-password",
                ),
                reset_token,
            )
            expires_at = (timezone.now() + timedelta(seconds=max_age)).strftime(
                "%d.%m.%Y %H:%M"
            )

            safe_delay(
                send_reset_password_email_task,
                user.id,
                reset_url,
                expires_at,
            )

        return Response(
            {
                "detail": _(
                    "Если пользователь с такой почтой существует, "
                    "инструкция по восстановлению будет отправлена."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    """Подтверждение восстановления пароля."""

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        token = (
            request.data.get("token") or request.query_params.get("token") or ""
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

        safe_delay(send_password_changed_email_task, user.id)

        return Response(
            {"detail": _("Пароль успешно обновлён.")},
            status=status.HTTP_200_OK,
        )


class ChangePasswordAPIView(APIView):
    """Смена пароля авторизованного пользователя."""

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
        safe_delay(send_password_changed_email_task, user.id)

        return Response(
            {"detail": _("Пароль успешно изменён.")},
            status=status.HTTP_200_OK,
        )
