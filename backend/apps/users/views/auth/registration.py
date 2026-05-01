from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user import CurrentUserSerializer
from apps.users.services.auth_services import build_verify_email_token
from apps.users.tasks import send_verify_email_task
from apps.users.views.auth.helpers import (
    get_frontend_url,
    get_register_serializer_class,
    safe_delay,
)


class RegisterAPIView(APIView):
    """Регистрация пользователя."""

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer_class = get_register_serializer_class(
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
        verify_url = get_frontend_url(
            getattr(settings, "FRONTEND_VERIFY_EMAIL_PATH", "/verify-email"),
            verify_token,
        )
        expires_at = (
            timezone.now() + timedelta(seconds=verify_expiry_seconds)
        ).strftime("%d.%m.%Y %H:%M")

        safe_delay(
            send_verify_email_task,
            user.id,
            verify_url,
            expires_at,
        )

        data = CurrentUserSerializer(
            user,
            context={"request": request},
        ).data
        return Response(data, status=status.HTTP_201_CREATED)
