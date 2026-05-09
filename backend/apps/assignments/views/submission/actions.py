from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsStudentSubmissionOwner
from apps.assignments.selectors import get_submission_by_id
from apps.assignments.serializers import (
    SubmissionDetailSerializer,
    SubmissionRetrySerializer,
    SubmissionSubmitSerializer,
)
from apps.assignments.services import (
    create_new_submission_attempt,
    submit_submission,
)
from apps.assignments.views.submission.common import validation_error_response


class SubmissionSubmitAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response(
                {"detail": "Сдача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, submission)

        serializer = SubmissionSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            submission = submit_submission(submission)
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionDetailSerializer(submission, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionRetryAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response(
                {"detail": "Сдача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, submission)

        serializer = SubmissionRetrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_submission = create_new_submission_attempt(submission)
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionDetailSerializer(
            new_submission,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_201_CREATED)
