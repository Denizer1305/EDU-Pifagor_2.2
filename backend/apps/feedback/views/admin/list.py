from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.selectors import get_feedback_requests_for_admin_queryset
from apps.feedback.serializers import FeedbackRequestListSerializer
from apps.feedback.views.admin.common import apply_feedback_filter
from apps.feedback.views.admin.permissions import IsAdminOrSuperuser

logger = logging.getLogger(__name__)


class FeedbackRequestAdminListAPIView(APIView):
    """Список обращений для администратора."""

    permission_classes = (IsAdminOrSuperuser,)

    def get(self, request, *args, **kwargs):
        logger.info(
            "FeedbackRequestAdminListAPIView.get called admin_user_id=%s",
            request.user.id,
        )

        queryset = get_feedback_requests_for_admin_queryset()
        queryset = apply_feedback_filter(request, queryset)

        serializer = FeedbackRequestListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
