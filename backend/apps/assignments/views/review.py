from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin, IsSubmissionOwnerOrReviewerOrAdmin
from apps.assignments.selectors import (
    get_review_comments_queryset,
    get_submission_answers_queryset,
    get_submission_by_id,
    get_submission_review_by_id,
    get_submission_reviews_queryset,
)
from apps.assignments.serializers import (
    ReviewCommentCreateSerializer,
    ReviewCommentSerializer,
    SubmissionAnswerReviewSerializer,
    SubmissionReviewApproveSerializer,
    SubmissionReviewDetailSerializer,
    SubmissionReviewListSerializer,
    SubmissionReviewRejectSerializer,
    SubmissionReviewReturnForRevisionSerializer,
    SubmissionReviewStartSerializer,
    SubmissionReviewSubmitSerializer,
)
from apps.assignments.services import (
    add_review_comment,
    approve_submission_review,
    reject_submission_review,
    return_submission_for_revision,
    review_submission_answer,
    start_submission_review,
    submit_submission_review,
)

logger = logging.getLogger(__name__)


def _validation_error_response(exc):
    if hasattr(exc, "message_dict"):
        payload = exc.message_dict
    elif hasattr(exc, "messages"):
        payload = {"detail": exc.messages}
    else:
        payload = {"detail": [str(exc)]}
    return Response(payload, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"detail": "Проверка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, review)

        serializer = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionReviewStartAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionReviewStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = start_submission_review(
                submission=submission,
                reviewer=request.user,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionAnswerReviewAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, submission_answer_id: int, *args, **kwargs):
        answer = get_submission_answers_queryset().filter(id=submission_answer_id).first()
        if answer is None:
            return Response({"detail": "Ответ не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and answer.submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionAnswerReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            answer = review_submission_answer(
                submission_answer=answer,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(
            answer.submission.review,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_200_OK)


class ReviewCommentCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_submission_review_by_id(review_id=review_id)
        if review is None:
            return Response({"detail": "Проверка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and review.submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = None
        if serializer.validated_data.get("question_id"):
            question = review.submission.assignment.questions.filter(
                id=serializer.validated_data["question_id"]
            ).first()

        submission_answer = None
        if serializer.validated_data.get("submission_answer_id"):
            submission_answer = review.submission.answers.filter(
                id=serializer.validated_data["submission_answer_id"]
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
            return _validation_error_response(exc)

        output = ReviewCommentSerializer(comment, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class SubmissionReviewSubmitAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_submission_review_by_id(review_id=review_id)
        if review is None:
            return Response({"detail": "Проверка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and review.submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionReviewSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = submit_submission_review(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionReviewReturnForRevisionAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_submission_review_by_id(review_id=review_id)
        if review is None:
            return Response({"detail": "Проверка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and review.submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionReviewReturnForRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = return_submission_for_revision(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionReviewApproveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_submission_review_by_id(review_id=review_id)
        if review is None:
            return Response({"detail": "Проверка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and review.submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionReviewApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = approve_submission_review(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionReviewRejectAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, review_id: int, *args, **kwargs):
        review = get_submission_review_by_id(review_id=review_id)
        if review is None:
            return Response({"detail": "Проверка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and review.submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionReviewRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = reject_submission_review(
                review=review,
                reviewer=request.user,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionReviewDetailSerializer(review, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)
