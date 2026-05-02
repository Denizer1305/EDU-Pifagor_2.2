from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    SubmissionAnswerReviewSerializer,
    SubmissionReviewDetailSerializer,
)
from apps.assignments.services import review_submission_answer
from apps.assignments.views.review.common import (
    get_submission_answer_or_none,
    validation_error_response,
)


class SubmissionAnswerReviewAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(
        self,
        request,
        answer_id: int | None = None,
        submission_answer_id: int | None = None,
        *args,
        **kwargs,
    ):
        """
        Проверяет отдельный ответ студента.

        Поддерживает оба имени параметра:
        - answer_id — используется в текущем urls.py
        - submission_answer_id — старое/внутреннее имя
        """

        actual_answer_id = answer_id or submission_answer_id
        answer = get_submission_answer_or_none(answer_id=actual_answer_id)

        if answer is None:
            return Response(
                {"detail": "Ответ не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.is_superuser
            and answer.submission.assignment.author_id != request.user.id
        ):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionAnswerReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            answer = review_submission_answer(
                submission_answer=answer,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(
            answer.submission.review,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_200_OK)
