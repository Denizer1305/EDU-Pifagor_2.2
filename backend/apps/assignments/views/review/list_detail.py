from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import (
    IsSubmissionOwnerOrReviewerOrAdmin,
    IsTeacherOrAdmin,
)
from apps.assignments.selectors import (
    get_submission_review_by_id,
    get_submission_reviews_queryset,
)
from apps.assignments.serializers import (
    SubmissionReviewDetailSerializer,
    SubmissionReviewListSerializer,
)


class SubmissionReviewListAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        queryset = get_submission_reviews_queryset(
            search=request.query_params.get("search", ""),
            review_status=request.query_params.get("review_status", ""),
            reviewer_id=request.query_params.get("reviewer_id") or None,
            submission_id=request.query_params.get("submission_id") or None,
        )

        if not request.user.is_superuser:
            queryset = queryset.filter(submission__assignment__author=request.user)

        serializer = SubmissionReviewListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionReviewDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsSubmissionOwnerOrReviewerOrAdmin)

    def get(self, request, pk: int, *args, **kwargs):
        review = get_submission_review_by_id(review_id=pk)
        if review is None:
            return Response(
                {"detail": "Проверка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, review)

        serializer = SubmissionReviewDetailSerializer(
            review,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
