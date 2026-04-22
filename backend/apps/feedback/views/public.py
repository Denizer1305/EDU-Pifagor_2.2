from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.filters import FeedbackRequestFilter
from apps.feedback.serializers import (
    FeedbackRequestCreateSerializer,
    FeedbackRequestDetailSerializer,
    FeedbackRequestErrorCreateSerializer,
    FeedbackRequestListSerializer,
)
from apps.feedback.selectors import (
    get_feedback_request_by_id,
    get_my_feedback_requests_queryset,
)
from apps.feedback.services.feedback_services import (
    create_contact_feedback_request,
    create_error_feedback_request,
)

logger = logging.getLogger(__name__)


def _get_request_files_list(request, field_name: str = "attachments") -> list:
    if hasattr(request, "FILES") and hasattr(request.FILES, "getlist"):
        return request.FILES.getlist(field_name)
    return []


def _build_serializer_input_data(request, *, field_name: str = "attachments"):
    data = request.data.copy()
    files = _get_request_files_list(request, field_name=field_name)

    if hasattr(data, "setlist"):
        data.setlist(field_name, files)
    else:
        data[field_name] = files

    return data


def _apply_feedback_filter(request, queryset):
    filterset = FeedbackRequestFilter(
        data=request.query_params,
        queryset=queryset,
    )

    if not filterset.is_valid():
        raise ValidationError(filterset.errors)

    return filterset.qs


class FeedbackRequestCreateAPIView(APIView):
    """
    Публичная форма обратной связи со страницы «Контакты».
    """

    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, *args, **kwargs):
        logger.info("FeedbackRequestCreateAPIView.post called")

        serializer_input = _build_serializer_input_data(request)
        serializer = FeedbackRequestCreateSerializer(
            data=serializer_input,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            feedback_request = create_contact_feedback_request(
                user=request.user if request.user.is_authenticated else None,
                subject=serializer.validated_data.get("subject", ""),
                message=serializer.validated_data["message"],
                full_name=serializer.validated_data.get("full_name", ""),
                email=serializer.validated_data.get("email", ""),
                phone=serializer.validated_data.get("phone", ""),
                organization_name=serializer.validated_data.get("organization_name", ""),
                type=serializer.validated_data.get("type"),
                is_personal_data_consent=serializer.validated_data["is_personal_data_consent"],
                files=serializer.validated_data.get("attachments", []),
                request=request,
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = FeedbackRequestDetailSerializer(
            feedback_request,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class FeedbackErrorCreateAPIView(APIView):
    """
    Создание bug-report из модального окна ошибки.
    Для авторизованного пользователя данные подтягиваются автоматически.
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, *args, **kwargs):
        logger.info(
            "FeedbackErrorCreateAPIView.post called user_id=%s",
            request.user.id,
        )

        serializer_input = _build_serializer_input_data(request)
        serializer = FeedbackRequestErrorCreateSerializer(
            data=serializer_input,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            feedback_request = create_error_feedback_request(
                user=request.user,
                subject=serializer.validated_data.get("subject", ""),
                message=serializer.validated_data["message"],
                type=serializer.validated_data.get("type"),
                is_personal_data_consent=serializer.validated_data["is_personal_data_consent"],
                files=serializer.validated_data.get("attachments", []),
                page_url=serializer.validated_data.get("page_url", ""),
                frontend_route=serializer.validated_data.get("frontend_route", ""),
                error_code=serializer.validated_data.get("error_code", ""),
                error_title=serializer.validated_data.get("error_title", ""),
                error_details=serializer.validated_data.get("error_details", ""),
                client_platform=serializer.validated_data.get("client_platform", ""),
                app_version=serializer.validated_data.get("app_version", ""),
                request=request,
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = FeedbackRequestDetailSerializer(
            feedback_request,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class MyFeedbackRequestListAPIView(APIView):
    """
    Список собственных обращений пользователя.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        logger.info(
            "MyFeedbackRequestListAPIView.get called user_id=%s",
            request.user.id,
        )

        queryset = get_my_feedback_requests_queryset(
            user=request.user,
        )
        queryset = _apply_feedback_filter(request, queryset)

        serializer = FeedbackRequestListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyFeedbackRequestDetailAPIView(APIView):
    """
    Детальный просмотр собственного обращения.
    """

    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk: int):
        feedback_request = get_feedback_request_by_id(
            feedback_request_id=pk,
        )
        if feedback_request is None:
            return None

        if feedback_request.user_id != request.user.id:
            return None

        return feedback_request

    def get(self, request, pk: int, *args, **kwargs):
        logger.info(
            "MyFeedbackRequestDetailAPIView.get called user_id=%s feedback_request_id=%s",
            request.user.id,
            pk,
        )

        feedback_request = self.get_object(request, pk)
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
