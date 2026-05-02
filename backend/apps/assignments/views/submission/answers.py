from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsStudentSubmissionOwner
from apps.assignments.selectors import get_submission_by_id
from apps.assignments.serializers import (
    SubmissionAnswerSaveSerializer,
    SubmissionDetailSerializer,
)
from apps.assignments.services import save_submission_answer
from apps.assignments.views.submission.common import (
    get_question,
    validation_error_response,
)


class SubmissionAnswerSaveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response(
                {"detail": "Сдача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, submission)

        serializer = SubmissionAnswerSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = get_question(serializer.validated_data["question_id"])
        if question is None:
            return Response(
                {"question_id": ["Вопрос не найден."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                selected_options_json=serializer.validated_data.get(
                    "selected_options_json"
                ),
                numeric_answer=serializer.validated_data.get("numeric_answer"),
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionDetailSerializer(
            answer.submission,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_200_OK)
