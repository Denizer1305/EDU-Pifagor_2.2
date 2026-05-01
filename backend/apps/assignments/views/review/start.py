from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    SubmissionReviewDetailSerializer,
    SubmissionReviewStartSerializer,
)
from apps.assignments.services import start_submission_review
from apps.assignments.views.review.common import (
    can_manage_submission,
    get_submission_or_none,
    validation_error_response,
)


class SubmissionReviewStartAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_or_none(submission_id=submission_id)
        if submission is None:
            return Response(
                {"detail": "Сдача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_submission(request.user, submission):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionReviewStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = start_submission_review(
                submission=submission,
                reviewer=request.user,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(
            review,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_200_OK)
