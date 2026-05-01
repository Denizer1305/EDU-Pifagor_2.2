from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    ReviewCommentCreateSerializer,
    ReviewCommentSerializer,
)
from apps.assignments.services import add_review_comment
from apps.assignments.views.review.common import (
    can_manage_submission_review,
    get_review_id_from_request,
    get_review_or_none,
    validation_error_response,
)


class ReviewCommentCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int | None = None, *args, **kwargs):
        actual_review_id = get_review_id_from_request(request, review_id)
        if actual_review_id is None:
            return Response(
                {"review_id": ["Необходимо передать id проверки."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = get_review_or_none(review_id=actual_review_id)
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

        serializer = ReviewCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = None
        if serializer.validated_data.get("question_id"):
            question = review.submission.assignment.questions.filter(
                id=serializer.validated_data["question_id"],
            ).first()

        submission_answer = None
        if serializer.validated_data.get("submission_answer_id"):
            submission_answer = review.submission.answers.filter(
                id=serializer.validated_data["submission_answer_id"],
            ).first()

        try:
            comment = add_review_comment(
                review=review,
                message=serializer.validated_data["message"],
                created_by=request.user,
                comment_type=serializer.validated_data.get("comment_type"),
                question=question,
                submission_answer=submission_answer,
                score_delta=serializer.validated_data.get("score_delta"),
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = ReviewCommentSerializer(comment, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)
