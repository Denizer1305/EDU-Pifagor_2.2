from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response

from apps.assignments.models import AssignmentQuestion, AssignmentVariant
from apps.assignments.selectors import get_assignment_publication_by_id


def validation_error_response(exc: DjangoValidationError | ValueError) -> Response:
    """Преобразует доменную ошибку в DRF Response."""

    if hasattr(exc, "message_dict"):
        payload = exc.message_dict
    elif hasattr(exc, "messages"):
        payload = {"detail": exc.messages}
    else:
        payload = {"detail": [str(exc)]}

    return Response(payload, status=status.HTTP_400_BAD_REQUEST)


def get_question(question_id):
    """Возвращает вопрос работы по id или None."""

    if not question_id:
        return None

    return AssignmentQuestion.objects.filter(pk=question_id).first()


def get_variant(variant_id):
    """Возвращает вариант работы по id или None."""

    if not variant_id:
        return None

    return AssignmentVariant.objects.filter(pk=variant_id).first()


def get_publication(publication_id):
    """Возвращает публикацию работы по id или None."""

    if not publication_id:
        return None

    return get_assignment_publication_by_id(publication_id=publication_id)
