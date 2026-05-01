from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsStudentSubmissionOwner
from apps.assignments.selectors import get_submission_by_id
from apps.assignments.serializers import (
    SubmissionAttachFileSerializer,
    SubmissionDetailSerializer,
)
from apps.assignments.services import attach_file_to_submission
from apps.assignments.views.submission.common import (
    get_question,
    validation_error_response,
)


class SubmissionAttachFileAPIView(APIView):
    permission_classes = (IsAuthenticated, IsStudentSubmissionOwner)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response(
                {"detail": "Сдача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, submission)

        serializer = SubmissionAttachFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = get_question(serializer.validated_data.get("question_id"))
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
            return validation_error_response(exc)

        refreshed = get_submission_by_id(submission_id=submission.id)
        output = SubmissionDetailSerializer(refreshed, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)
