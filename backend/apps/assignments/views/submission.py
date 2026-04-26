from __future__ import annotations

import logging

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import (
    IsStudentSubmissionOwner,
    IsSubmissionOwnerOrReviewerOrAdmin,
    is_admin,
    is_teacher,
)
from apps.assignments.selectors import (
    get_available_publications_for_student_queryset,
    get_student_submissions_queryset,
    get_submission_by_id,
    get_submissions_queryset,
)
from apps.assignments.serializers import (
    SubmissionAnswerSaveSerializer,
    SubmissionAttachFileSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
    SubmissionRetrySerializer,
    SubmissionStartSerializer,
    SubmissionSubmitSerializer,
)
from apps.assignments.services import (
    attach_file_to_submission,
    create_new_submission_attempt,
    save_submission_answer,
    start_submission,
    submit_submission,
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


def _get_question(question_id):
    from apps.assignments.models import AssignmentQuestion

    return AssignmentQuestion.objects.filter(pk=question_id).first()


def _get_variant(variant_id):
    from apps.assignments.models import AssignmentVariant

    if not variant_id:
        return None
    return AssignmentVariant.objects.filter(pk=variant_id).first()


def _get_publication(publication_id):
    from apps.assignments.selectors import get_assignment_publication_by_id

    if not publication_id:
        return None
    return get_assignment_publication_by_id(publication_id=publication_id)


class SubmissionListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        logger.info("SubmissionListAPIView.get called user_id=%s", request.user.id)

        if is_teacher(request.user) or is_admin(request.user):
            queryset = get_submissions_queryset(
                search=request.query_params.get("search", ""),
                status=request.query_params.get("status", ""),
                assignment_id=request.query_params.get("assignment_id") or None,
                publication_id=request.query_params.get("publication_id") or None,
                student_id=request.query_params.get("student_id") or None,
                checked_by_id=request.query_params.get("checked_by_id") or None,
            )

            if not request.user.is_superuser:
                queryset = queryset.filter(assignment__author=request.user)
        else:
            queryset = get_student_submissions_queryset(
                student=request.user,
                search=request.query_params.get("search", ""),
                status=request.query_params.get("status", ""),
                course_id=request.query_params.get("course_id") or None,
                lesson_id=request.query_params.get("lesson_id") or None,
            )

        serializer = SubmissionListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsSubmissionOwnerOrReviewerOrAdmin)

    def get_object(self, request, pk: int):
        submission = get_submission_by_id(submission_id=pk)
        if submission is None:
            return None
        self.check_object_permissions(request, submission)
        return submission

    def get(self, request, pk: int, *args, **kwargs):
        submission = self.get_object(request, pk)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubmissionDetailSerializer(
            submission,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionStartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = SubmissionStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        publication = _get_publication(serializer.validated_data["publication_id"])
        if publication is None:
            return Response({"publication_id": ["Публикация не найдена."]}, status=status.HTTP_400_BAD_REQUEST)

        available_ids = get_available_publications_for_student_queryset(student=request.user).values_list("id", flat=True)
        if publication.id not in available_ids:
            return Response({"detail": "Эта работа недоступна пользователю."}, status=status.HTTP_403_FORBIDDEN)

        variant = _get_variant(serializer.validated_data.get("variant_id"))
        if variant is not None and variant.assignment_id != publication.assignment_id:
            return Response({"variant_id": ["Вариант не принадлежит выбранной работе."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = start_submission(
                publication=publication,
                student=request.user,
                variant=variant,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionDetailSerializer(submission, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class SubmissionAnswerSaveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, submission)

        serializer = SubmissionAnswerSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = _get_question(serializer.validated_data["question_id"])
        if question is None:
            return Response({"question_id": ["Вопрос не найден."]}, status=status.HTTP_400_BAD_REQUEST)

        if question.assignment_id != submission.assignment_id:
            return Response(
                {"question_id": ["Вопрос не относится к этой работе."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            answer = save_submission_answer(
                submission=submission,
                question=question,
                answer_text=serializer.validated_data.get("answer_text", ""),
                answer_json=serializer.validated_data.get("answer_json"),
                selected_options_json=serializer.validated_data.get("selected_options_json"),
                numeric_answer=serializer.validated_data.get("numeric_answer"),
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionDetailSerializer(answer.submission, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionAttachFileAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, submission)

        serializer = SubmissionAttachFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = _get_question(serializer.validated_data.get("question_id"))
        if question is not None and question.assignment_id != submission.assignment_id:
            return Response(
                {"question_id": ["Вопрос не относится к этой работе."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            attach_file_to_submission(
                submission=submission,
                file=serializer.validated_data["file"],
                question=question,
                attachment_type=serializer.validated_data.get("attachment_type"),
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        refreshed = get_submission_by_id(submission_id=submission.id)
        output = SubmissionDetailSerializer(refreshed, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionSubmitAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, submission)

        serializer = SubmissionSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            submission = submit_submission(submission)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionDetailSerializer(submission, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class SubmissionRetryAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, submission)

        serializer = SubmissionRetrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_submission = create_new_submission_attempt(submission)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = SubmissionDetailSerializer(new_submission, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)
