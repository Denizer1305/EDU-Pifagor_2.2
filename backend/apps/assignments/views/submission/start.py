from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.selectors import get_available_publications_for_student_queryset
from apps.assignments.serializers import (
    SubmissionDetailSerializer,
    SubmissionStartSerializer,
)
from apps.assignments.services import start_submission
from apps.assignments.views.submission.common import (
    get_publication,
    get_variant,
    validation_error_response,
)


class SubmissionStartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = SubmissionStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        publication = get_publication(serializer.validated_data["publication_id"])
        if publication is None:
            return Response(
                {"publication_id": ["Публикация не найдена."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        available_ids = get_available_publications_for_student_queryset(
            student=request.user,
        ).values_list("id", flat=True)

        if publication.id not in available_ids:
            return Response(
                {"detail": "Эта работа недоступна пользователю."},
                status=status.HTTP_403_FORBIDDEN,
            )

        variant = get_variant(serializer.validated_data.get("variant_id"))
        if variant is not None and variant.assignment_id != publication.assignment_id:
            return Response(
                {"variant_id": ["Вариант не принадлежит выбранной работе."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            submission = start_submission(
                publication=publication,
                student=request.user,
                variant=variant,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = SubmissionDetailSerializer(submission, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)
