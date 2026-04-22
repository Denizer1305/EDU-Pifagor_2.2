from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.filters import FeedbackRequestFilter
from apps.feedback.serializers import (
    FeedbackRequestAdminUpdateSerializer,
    FeedbackRequestDetailSerializer,
    FeedbackRequestListSerializer,
)
from apps.feedback.selectors import (
    get_feedback_request_by_id,
    get_feedback_requests_for_admin_queryset,
)
from apps.feedback.services import (
    archive_feedback_request,
    mark_feedback_as_spam,
    mark_feedback_in_progress,
    reject_feedback_request,
    resolve_feedback_request,
)
from apps.users.constants import ROLE_ADMIN

logger = logging.getLogger(__name__)


def _get_user_role_codes(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_ADMIN}

    if not hasattr(user, "user_roles"):
        return set()

    queryset = user.user_roles.all()
    model_fields = {field.name for field in queryset.model._meta.get_fields()}
    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def _is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


def _apply_feedback_filter(request, queryset):
    filterset = FeedbackRequestFilter(
        data=request.query_params,
        queryset=queryset,
    )

    if not filterset.is_valid():
        raise ValidationError(filterset.errors)

    return filterset.qs


class IsAdminOrSuperuser(BasePermission):
    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return _is_admin(request.user)


class FeedbackRequestAdminListAPIView(APIView):
    """
    Список обращений для администратора.
    """

    permission_classes = (IsAdminOrSuperuser,)

    def get(self, request, *args, **kwargs):
        logger.info(
            "FeedbackRequestAdminListAPIView.get called admin_user_id=%s",
            request.user.id,
        )

        queryset = get_feedback_requests_for_admin_queryset()
        queryset = _apply_feedback_filter(request, queryset)

        serializer = FeedbackRequestListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedbackRequestAdminDetailAPIView(APIView):
    """
    Детальный просмотр и обработка обращения администратором.
    PATCH:
    - status=in_progress -> взять в работу
    - status=resolved -> решить
    - status=rejected -> отклонить
    - status=spam -> пометить как спам
    - status=archived -> архивировать
    - без status -> обновить комментарии/флаги
    """

    permission_classes = (IsAdminOrSuperuser,)

    def get_object(self, pk: int):
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
            feedback_request,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        status_value = validated.get("status")
        reply_message = validated.get("reply_message", "")
        internal_note = validated.get("internal_note", "")

        try:
            if status_value == feedback_request.StatusChoices.IN_PROGRESS:
                feedback_request = mark_feedback_in_progress(
                    feedback_request=feedback_request,
                    admin_user=request.user,
                    internal_note=internal_note,
                )
            elif status_value == feedback_request.StatusChoices.RESOLVED:
                feedback_request = resolve_feedback_request(
                    feedback_request=feedback_request,
                    admin_user=request.user,
                    reply_message=reply_message,
                    internal_note=internal_note,
                )
            elif status_value == feedback_request.StatusChoices.REJECTED:
                feedback_request = reject_feedback_request(
                    feedback_request=feedback_request,
                    admin_user=request.user,
                    reply_message=reply_message,
                    internal_note=internal_note,
                )
            elif status_value == feedback_request.StatusChoices.SPAM:
                feedback_request = mark_feedback_as_spam(
                    feedback_request=feedback_request,
                    admin_user=request.user,
                    internal_note=internal_note,
                )
            elif status_value == feedback_request.StatusChoices.ARCHIVED:
                feedback_request = archive_feedback_request(
                    feedback_request=feedback_request,
                    admin_user=request.user,
                    internal_note=internal_note,
                )
            else:
                direct_fields = (
                    "reply_message",
                    "internal_note",
                    "is_spam_suspected",
                    "is_processed",
                )
                update_fields: list[str] = []

                for field_name in direct_fields:
                    if field_name in validated:
                        setattr(feedback_request, field_name, validated[field_name])
                        update_fields.append(field_name)

                if "is_processed" in validated:
                    if validated["is_processed"]:
                        if not feedback_request.processed_at:
                            feedback_request.processed_at = timezone.now()
                            update_fields.append("processed_at")
                        if not feedback_request.processed_by_id:
                            feedback_request.processed_by = request.user
                            update_fields.append("processed_by")
                    else:
                        feedback_request.processed_at = None
                        feedback_request.processed_by = None
                        update_fields.extend(["processed_at", "processed_by"])

                feedback_request.full_clean()
                if update_fields:
                    if "updated_at" not in update_fields:
                        update_fields.append("updated_at")
                    feedback_request.save(update_fields=update_fields)
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = FeedbackRequestDetailSerializer(
            feedback_request,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
