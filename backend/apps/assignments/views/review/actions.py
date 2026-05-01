from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    SubmissionReviewApproveSerializer,
    SubmissionReviewDetailSerializer,
    SubmissionReviewRejectSerializer,
    SubmissionReviewReturnForRevisionSerializer,
    SubmissionReviewSubmitSerializer,
)
from apps.assignments.services import (
    approve_submission_review,
    reject_submission_review,
    return_submission_for_revision,
    submit_submission_review,
)
from apps.assignments.views.review.common import (
    can_manage_submission_review,
    get_review_or_none,
    validation_error_response,
)


class SubmissionReviewSubmitAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_review_or_none(review_id=review_id)
        if review is None:
            return Response(
                {"detail": "Проверка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_submission_review(request.user, review):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionReviewSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = submit_submission_review(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionReviewReturnForRevisionAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_review_or_none(review_id=review_id)
        if review is None:
            return Response(
                {"detail": "Проверка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_submission_review(request.user, review):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionReviewReturnForRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = return_submission_for_revision(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionReviewApproveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_review_or_none(review_id=review_id)
        if review is None:
            return Response(
                {"detail": "Проверка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_submission_review(request.user, review):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionReviewApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = approve_submission_review(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionReviewRejectAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_review_or_none(review_id=review_id)
        if review is None:
            return Response(
                {"detail": "Проверка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_submission_review(request.user, review):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionReviewRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = reject_submission_review(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)
