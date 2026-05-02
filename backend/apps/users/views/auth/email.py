from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services.auth_services import verify_user_email_by_token
from apps.users.tasks import send_welcome_email_task
from apps.users.views.auth.helpers import safe_delay


class VerifyEmailAPIView(APIView):
    """Подтверждение email пользователя."""

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        token = (
            request.data.get("token") or request.query_params.get("token") or ""
        ).strip()

        if not token:
            raise ValidationError({"token": _("Не передан токен подтверждения.")})

        user = verify_user_email_by_token(token)
        safe_delay(send_welcome_email_task, user.id)

        return Response(
            {"detail": _("Электронная почта успешно подтверждена.")},
            status=status.HTTP_200_OK,
        )
