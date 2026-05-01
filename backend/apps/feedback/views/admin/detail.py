from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.selectors import get_feedback_request_by_id
from apps.feedback.serializers import (
    FeedbackRequestAdminUpdateSerializer,
    FeedbackRequestDetailSerializer,
)
from apps.feedback.views.admin.common import django_validation_error_payload
from apps.feedback.views.admin.permissions import IsAdminOrSuperuser
from apps.feedback.views.admin.processing import (
    apply_status_action,
    update_processing_fields,
)

logger = logging.getLogger(__name__)


class FeedbackRequestAdminDetailAPIView(APIView):
    """
    Детальный просмотр и обработка обращения администратором.

    PATCH:
    - status=in_progress -> взять в работу;
    - status=resolved -> решить;
    - status=rejected -> отклонить;
    - status=spam -> пометить как спам;
    - status=archived -> архивировать;
    - без status -> обновить processing-поля.
    """

    permission_classes = (IsAdminOrSuperuser,)

    def get_object(self, pk: int):
        """Возвращает обращение по id."""

        return get_feedback_request_by_id(
            feedback_request_id=pk,
        )

    def get(self, request, pk: int, *args, **kwargs):
        logger.info(
            "FeedbackRequestAdminDetailAPIView.get called admin_user_id=%s feedback_request_id=%s",
            request.user.id,
            pk,
        )

        feedback_request = self.get_object(pk)
        if feedback_request is None:
            return Response(
                {"detail": "Обращение не найдено."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FeedbackRequestDetailSerializer(
            feedback_request,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        logger.info(
            "FeedbackRequestAdminDetailAPIView.patch called admin_user_id=%s feedback_request_id=%s",
            request.user.id,
            pk,
        )

        feedback_request = self.get_object(pk)
        if feedback_request is None:
            return Response(
                {"detail": "Обращение не найдено."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FeedbackRequestAdminUpdateSerializer(
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        status_value = validated_data.get("status")
        reply_message = validated_data.get("reply_message", "")
        internal_note = validated_data.get("internal_note", "")

        try:
            updated_feedback_request = apply_status_action(
                feedback_request=feedback_request,
                admin_user=request.user,
                status_value=status_value,
                reply_message=reply_message,
                internal_note=internal_note,
            )

            if updated_feedback_request is None:
                update_processing_fields(
                    feedback_request=feedback_request,
                    admin_user=request.user,
                    validated_data=validated_data,
                )

        except DjangoValidationError as exc:
            return Response(
                django_validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback_request = self.get_object(pk)
        output_serializer = FeedbackRequestDetailSerializer(
            feedback_request,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
